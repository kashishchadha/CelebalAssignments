import os
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, sha2, concat_ws, lit, when, date_format, year, month, quarter,
    dayofmonth, dayofweek, weekofyear, sum as spark_sum, count as spark_count,
    avg as spark_avg, round as spark_round, coalesce, to_date
)
from config.settings import GOLD_DIR, SILVER_DIR

class GoldLayer:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def _generate_dim_date(self) -> DataFrame:
        df = self.spark.sql("SELECT explode(sequence(to_date('2023-01-01'), to_date('2026-12-31'), interval 1 day)) as date_key")
        return df.select(
            col("date_key"),
            year(col("date_key")).alias("year"),
            quarter(col("date_key")).alias("quarter"),
            month(col("date_key")).alias("month"),
            date_format(col("date_key"), "MMMM").alias("month_name"),
            dayofmonth(col("date_key")).alias("day"),
            dayofweek(col("date_key")).alias("day_of_week"),
            weekofyear(col("date_key")).alias("week_of_year"),
            when(dayofweek(col("date_key")).isin([1, 7]), True).otherwise(False).alias("is_weekend")
        )

    def process_to_gold(self, silver_paths: dict) -> dict:
        gold_outputs = {}

        customers_df = self.spark.read.format("delta").load(silver_paths["customers"])
        stores_df = self.spark.read.format("delta").load(silver_paths["stores"])
        products_df = self.spark.read.format("delta").load(silver_paths["products"])
        orders_df = self.spark.read.format("delta").load(silver_paths["orders"])
        order_items_df = self.spark.read.format("delta").load(silver_paths["order_items"])
        returns_df = self.spark.read.format("delta").load(silver_paths["product_returns"])
        interactions_df = self.spark.read.format("delta").load(silver_paths["customer_interactions"])

        dim_date_df = self._generate_dim_date()
        dim_date_path = os.path.join(str(GOLD_DIR), "dim_date")
        dim_date_df.write.format("delta").mode("overwrite").save(dim_date_path)
        gold_outputs["dim_date"] = dim_date_path

        dim_customer_df = customers_df.withColumn(
            "customer_sk",
            coalesce(col("surrogate_key"), sha2(concat_ws("||", col("customer_id"), col("effective_start_date")), 256))
        ).withColumn(
            "churn_risk_band",
            when(col("churn_risk_score") >= 0.7, "High Risk")
            .when(col("churn_risk_score") >= 0.4, "Medium Risk")
            .otherwise("Low Risk")
        ).select(
            "customer_sk", "customer_id", "first_name", "last_name", "email",
            "phone", "city", "state", "country", "segment", "churn_risk_score",
            "churn_risk_band", "is_current", "effective_start_date", "effective_end_date"
        )
        dim_customer_path = os.path.join(str(GOLD_DIR), "dim_customer")
        dim_customer_df.write.format("delta").mode("overwrite").save(dim_customer_path)
        gold_outputs["dim_customer"] = dim_customer_path

        dim_product_df = products_df.withColumn(
            "product_sk", sha2(col("product_id"), 256)
        ).select(
            "product_sk", "product_id", "product_name", "category",
            "subcategory", "unit_cost", "msrp", "quality_rating"
        )
        dim_product_path = os.path.join(str(GOLD_DIR), "dim_product")
        dim_product_df.write.format("delta").mode("overwrite").save(dim_product_path)
        gold_outputs["dim_product"] = dim_product_path

        dim_store_df = stores_df.withColumn(
            "store_sk", sha2(col("store_id"), 256)
        ).select(
            "store_sk", "store_id", "store_name", "store_type",
            "city", "region", "sqft_area", "manager_name", "opened_date"
        )
        dim_store_path = os.path.join(str(GOLD_DIR), "dim_store")
        dim_store_df.write.format("delta").mode("overwrite").save(dim_store_path)
        gold_outputs["dim_store"] = dim_store_path

        active_customers = dim_customer_df.filter(col("is_current") == True)

        fact_sales_df = order_items_df.alias("itm").join(
            orders_df.alias("ord"), on="order_id", how="inner"
        ).join(
            active_customers.alias("cust"), on="customer_id", how="left"
        ).join(
            dim_product_df.alias("prod"), on="product_id", how="left"
        ).join(
            dim_store_df.alias("str"), on="store_id", how="left"
        ).withColumn(
            "date_key", to_date(col("ord.order_timestamp"))
        ).withColumn(
            "gross_sales_amount", spark_round(col("itm.quantity") * col("itm.unit_price"), 2)
        ).withColumn(
            "net_sales_amount", spark_round((col("itm.quantity") * col("itm.unit_price")) - col("itm.discount_amount"), 2)
        ).withColumn(
            "total_cost", spark_round(col("itm.quantity") * coalesce(col("prod.unit_cost"), lit(0.0)), 2)
        ).withColumn(
            "profit_amount", spark_round(col("net_sales_amount") - col("total_cost"), 2)
        ).withColumn(
            "profit_margin_pct",
            when(col("net_sales_amount") > 0, spark_round((col("profit_amount") / col("net_sales_amount")) * 100, 2)).otherwise(0.0)
        ).select(
            col("itm.item_id"),
            col("ord.order_id"),
            col("cust.customer_sk"),
            col("prod.product_sk"),
            col("str.store_sk"),
            col("date_key"),
            col("ord.order_status"),
            col("ord.payment_method"),
            col("itm.quantity"),
            col("itm.unit_price"),
            col("gross_sales_amount"),
            col("itm.discount_amount"),
            col("itm.tax_amount"),
            col("net_sales_amount"),
            col("profit_amount"),
            col("profit_margin_pct")
        )

        fact_sales_path = os.path.join(str(GOLD_DIR), "fact_sales")
        fact_sales_df.write.format("delta").mode("overwrite").save(fact_sales_path)
        gold_outputs["fact_sales"] = fact_sales_path

        fact_returns_df = returns_df.alias("ret").join(
            active_customers.alias("cust"), on="customer_id", how="left"
        ).join(
            dim_product_df.alias("prod"), on="product_id", how="left"
        ).withColumn(
            "return_date_key", to_date(col("ret.return_timestamp"))
        ).select(
            col("ret.return_id"),
            col("ret.order_id"),
            col("ret.item_id"),
            col("cust.customer_sk"),
            col("prod.product_sk"),
            col("return_date_key"),
            col("ret.return_reason"),
            col("ret.refund_amount")
        )

        fact_returns_path = os.path.join(str(GOLD_DIR), "fact_returns")
        fact_returns_df.write.format("delta").mode("overwrite").save(fact_returns_path)
        gold_outputs["fact_returns"] = fact_returns_path

        sales_performance_mart = fact_sales_df.alias("fs").join(
            dim_store_df.alias("ds"), "store_sk"
        ).join(
            dim_product_df.alias("dp"), "product_sk"
        ).join(
            dim_date_df.alias("dd"), fact_sales_df.date_key == dim_date_df.date_key
        ).groupBy(
            col("ds.region"), col("ds.store_name"), col("dp.category"),
            col("dd.year"), col("dd.month_name")
        ).agg(
            spark_sum("fs.net_sales_amount").alias("total_net_sales"),
            spark_sum("fs.gross_sales_amount").alias("total_gross_sales"),
            spark_sum("fs.discount_amount").alias("total_discounts"),
            spark_count("fs.order_id").alias("total_orders"),
            spark_sum("fs.quantity").alias("total_units_sold"),
            spark_avg("fs.profit_margin_pct").alias("avg_profit_margin_pct")
        )
        sales_mart_path = os.path.join(str(GOLD_DIR), "gold_sales_performance_mart")
        sales_performance_mart.write.format("delta").mode("overwrite").save(sales_mart_path)
        gold_outputs["gold_sales_performance_mart"] = sales_mart_path

        customer_churn_mart = dim_customer_df.filter(col("is_current") == True).alias("dc").join(
            interactions_df.groupBy("customer_id").agg(spark_sum("support_tickets_count").alias("total_tickets")),
            on="customer_id", how="left"
        ).groupBy(
            col("dc.segment"), col("dc.city"), col("dc.churn_risk_band")
        ).agg(
            spark_count("dc.customer_id").alias("customer_count"),
            spark_avg("dc.churn_risk_score").alias("avg_churn_risk_score"),
            coalesce(spark_sum("total_tickets"), lit(0)).alias("total_support_tickets")
        )
        churn_mart_path = os.path.join(str(GOLD_DIR), "gold_customer_churn_mart")
        customer_churn_mart.write.format("delta").mode("overwrite").save(churn_mart_path)
        gold_outputs["gold_customer_churn_mart"] = churn_mart_path

        product_quality_mart = dim_product_df.alias("dp").join(
            fact_sales_df.groupBy("product_sk").agg(
                spark_sum("quantity").alias("total_units_sold")
            ), on="product_sk", how="left"
        ).join(
            fact_returns_df.groupBy("product_sk").agg(
                spark_count("return_id").alias("total_returns"),
                spark_sum("refund_amount").alias("total_refund_amount")
            ), on="product_sk", how="left"
        ).groupBy(
            col("dp.category"), col("dp.subcategory"), col("dp.product_name")
        ).agg(
            coalesce(spark_sum("total_units_sold"), lit(0)).alias("units_sold"),
            coalesce(spark_sum("total_returns"), lit(0)).alias("return_count"),
            coalesce(spark_sum("total_refund_amount"), lit(0.0)).alias("refund_amount"),
            spark_avg("dp.quality_rating").alias("avg_quality_rating")
        ).withColumn(
            "return_rate_pct",
            when(col("units_sold") > 0, spark_round((col("return_count") / col("units_sold")) * 100, 2)).otherwise(0.0)
        )
        quality_mart_path = os.path.join(str(GOLD_DIR), "gold_product_quality_mart")
        product_quality_mart.write.format("delta").mode("overwrite").save(quality_mart_path)
        gold_outputs["gold_product_quality_mart"] = quality_mart_path

        store_analytics_mart = dim_store_df.alias("ds").join(
            fact_sales_df.groupBy("store_sk").agg(
                spark_sum("net_sales_amount").alias("total_revenue"),
                spark_count("order_id").alias("total_orders"),
                spark_avg("net_sales_amount").alias("avg_order_value")
            ), on="store_sk", how="left"
        ).groupBy(
            col("ds.store_id"), col("ds.store_name"), col("ds.region"),
            col("ds.store_type"), col("ds.sqft_area")
        ).agg(
            coalesce(spark_sum("total_revenue"), lit(0.0)).alias("total_revenue"),
            coalesce(spark_sum("total_orders"), lit(0)).alias("total_orders"),
            coalesce(spark_avg("avg_order_value"), lit(0.0)).alias("avg_order_value")
        ).withColumn(
            "revenue_per_sqft",
            when(col("sqft_area") > 0, spark_round(col("total_revenue") / col("sqft_area"), 2)).otherwise(0.0)
        )
        store_mart_path = os.path.join(str(GOLD_DIR), "gold_store_analytics_mart")
        store_analytics_mart.write.format("delta").mode("overwrite").save(store_mart_path)
        gold_outputs["gold_store_analytics_mart"] = store_analytics_mart

        return gold_outputs
