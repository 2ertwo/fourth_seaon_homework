# Generated by Django 4.2.4 on 2023-08-08 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MetricsData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("turbine_id", models.SmallIntegerField(verbose_name="风机id")),
                ("model_name", models.TextField(verbose_name="模型名称")),
                ("score_name", models.TextField(verbose_name="评估指标名称")),
                ("target_name", models.TextField(verbose_name="预测指标名称")),
                ("score", models.FloatField(verbose_name="值")),
            ],
        ),
        migrations.CreateModel(
            name="PredictData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("turbine_id", models.SmallIntegerField(verbose_name="风机id")),
                ("data_time", models.DateTimeField(verbose_name="时间")),
                ("model_name", models.TextField(verbose_name="模型名称")),
                ("target_name", models.TextField(verbose_name="预测指标名称")),
                ("value", models.FloatField(verbose_name="预测值")),
            ],
        ),
        migrations.CreateModel(
            name="TurbinesData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("turbine_id", models.SmallIntegerField(verbose_name="风机id")),
                ("data_time", models.DateTimeField(verbose_name="时间")),
                ("wind_speed", models.FloatField(verbose_name="预测风速")),
                ("pre_power", models.FloatField(verbose_name="预测功率（系统生成）")),
                ("wind_direction", models.FloatField(verbose_name="风向")),
                ("temperature", models.FloatField(verbose_name="温度")),
                ("humidity", models.FloatField(verbose_name="湿度")),
                ("pressure", models.FloatField(verbose_name="气压")),
                ("round_a_ws", models.FloatField(verbose_name="实际风速")),
                ("round_a_power", models.FloatField(verbose_name="实际功率（计量口径一）")),
                ("yd15", models.FloatField(verbose_name="实际功率（计量口径二）")),
            ],
        ),
    ]
