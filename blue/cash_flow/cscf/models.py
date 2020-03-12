from django.db import models


class Companies(models.Model):
    """
    Model which holds metadata about the companies (in this case, just need the ticker symbol)
    """
    stock_symbol = models.CharField(primary_key=True, max_length=4, null=False)

    class Meta:
        db_table = 'companies'


class CashFlowData(models.Model):
    """
    Holds the data found for each company's 10-K filing.
    """
    id = models.AutoField(primary_key=True)
    stock_symbol = models.ForeignKey('Companies', models.CASCADE, null=False)
    is_header = models.SmallIntegerField(null=False)
    filing = models.CharField(max_length=500, null=False)
    first_previous_year = models.IntegerField(null=True)
    second_previous_year = models.IntegerField(null=True)
    third_previous_year = models.IntegerField(null=True)

    class Meta:
        db_table = 'cash_flow'
