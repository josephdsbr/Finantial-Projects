import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import psycopg2

""" Function which is going to calculate the factor to the final client """

def CalculateClientCoefficientFactor(installment, flatRate, client):
    factor = (1 + flatRate)**(installment) if client == True else 1
    return factor

""" Function which is going to calculate the factor to the merchant """

def CalculateMerchantCoefficientFactor(installment, flatRate, client):
    factor = (1 + flatRate)**(installment) if client == False else 1

""" Function to calculate the final value to the final client """

def ClientValue(installment, flatRate, value, client, fix_value = 0):
    factor = CalculateClientCoefficientFactor(installment, flatRate, client)
    client_value = value*factor
    return client_value + fix_value

""" Function to calculate the final value to the merchant """

def MerchantValue(installment, flatRate, value, client, fix_value = 0):
    factor = CalculateMerchantCoefficientFactor(installment, flatRate, client)
    merchant_value = value*factor
    return merchant_value + fix_value

""" Creating a function which add days """

def add_days(x, d, k = 0, t = 1):
    date = x
    new_date = date + timedelta(days = (k + d*t))
    iso_date = new_date
    return new_date

""" Creating a function which is going to Help in SPay function """

def week_step(x, m, di = 3):
    floor_date = x - timedelta(days = x.weekday())
    new_date = floor_date + timedelta(days = di + 7*m)
    return new_date.date()

""" A payment modality which calculates the payment_date based on split of transactions into payment fluxs """

def InstallmentPayment(date, type, installment, credit_days = 30, debit_days = 2):
    payment_date = add_days(date, d = credit_days, t = installment) if type == 'CREDIT' else add_days(x, d = debit_days)
    return payment_date()
""" A payment modality which antecipates the payments """

def AntecipationPayment(date, type, credit_days = 0, debit_days = 2):
    payment_date = add_days(date, credit_days) if type == 'CREDIT' else add_days(date, debit_days)
    return payment_date

def AntecipationFactor(n, i):
    factor = ((1 + i)**n - 1)/((1+i)**n*i)
    return factor

def AntecipacitonRate(payment_date, payment_exp_date, antecipation_rate, installmentValue):
    # diferences between the expected day of payment and the day of antecipation
    n = (payment_exp_date - payment_date).days/30
    factor = AntecipationFactor(n, antecipation_rate)
    ant_value = factor*installmentValue
    return ant_value
