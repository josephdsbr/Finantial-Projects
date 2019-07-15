import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import psycopg2
import json

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

def AntPayment(date, type, credit_days = 0, debit_days = 2):
    payment_date = add_days(date, credit_days) if type == 'CREDIT' else add_days(date, debit_days)
    return payment_date

def AntFactor(n, i):
    factor = ((1 + i)**n - 1)/((1+i)**n*i)
    return factor

def AntValue(payment_date, payment_exp_date, antecipation_rate, installmentValue):
    # diferences between the expected day of payment and the day of antecipation
    n = (payment_exp_date - payment_date).days/30
    factor = AntFactor(n, antecipation_rate)
    ant_value = factor*installmentValue
    return ant_value

class transaction():
    def __init__(self, json_file):
        """

        Loading the JSON file into our class
        
        """
        self.data = json.load(open(json_file, 'r', encoding = 'utf-8'))

        """

        Separating some characteristics of the transaction into the class attributes
        
        """

        
        self.flatRate = self.data["merchant"]["flatRate"]
        self.fix_value = self.data["merchant"]["fix_value"]
        self.client = self.data["merchant"]["client"]
        self.antRate = self.data["merchant"]["antRate"]

        self.date = datetime.strptime(self.data["transaction"]["date"], "%Y-%m-%d %H:%M:%S")
        self.type = self.data["transaction"]["type"]
        self.antecipation = self.data["transaction"]["antecipation"]
        self.value = self.data["transaction"]["value"]
        self.installment = self.data["transaction"]["installment"] 

        """ Creating new features from the existing informations """

        self.installmentValue = self.value/self.installment
        self.dateLastPayment = (self.date + timedelta(days = 30*self.installment))
        self.datePayment = self.date + timedelta(days = 1)
        self.antValue = AntValue(self.datePayment, self.dateLastPayment, self.antRate, self.installmentValue)

t = transaction('dt.json')