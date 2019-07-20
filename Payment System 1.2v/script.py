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

""" Function to calculate the final value to the final client """

def ClientValue(installment, flatRate, value, client, fix_value = 0):
    factor = CalculateClientCoefficientFactor(installment, flatRate, client)
    client_value = value*factor
    return client_value + fix_value

""" Function to calculate the payment value to the merchant """

def MerchantValue(installment, flatRate, value, client, fix_value = 0):
    cv = ClientValue(installment, flatRate, value, client, fix_value) - fix_value
    factor = (1 + flatRate)**(installment)
    merchantValue = round(cv/factor,2)
    return merchantValue

""" Creating a function which add days """

def add_days(x, d, k = 0, t = 1):
    date = x
    new_date = date + timedelta(days = (k + d*t))
    iso_date = new_date
    return new_date

""" A payment modality which calculates the payment_date based on split of transactions into payment fluxs """
def AntFactor(n, i):
    factor = ((1 + i)**n - 1)/((1+i)**n*i)
    return factor

def AntPayment(date, type, credit_days = 0, debit_days = 2):
    payment_date = add_days(date, credit_days) if type == 'CREDIT' else add_days(date, debit_days)
    return payment_date
    
def datePayment(date, installment, type):
    payment_date = [add_days(x = date, d = 30, t = i).date() for i in range(1, installment + 1)] if type == 'credit' else add_days(x = date, d = 2).date()
    return payment_date

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
        self.clientName = self.data["merchant"]["merchantName"]
        self.clientId = self.data["merchant"]["merchantIdentifier"]
        self.client = self.data["merchant"]["client"]
        self.antRate = self.data["merchant"]["antRate"]

        self.date = datetime.strptime(self.data["transaction"]["date"], "%Y-%m-%d %H:%M:%S")
        self.installment = self.data['transaction']['installment']
        self.type = self.data["transaction"]["type"]
        self.antecipation = self.data["transaction"]["antecipation"]
        self.value = self.data["transaction"]["value"]
        self.clientValue = ClientValue(self.installment, self.flatRate, self.value, self.client, self.fix_value)
        self.merchantValue = MerchantValue(self.installment, self.flatRate, self.value, self.client, self.fix_value)
        self.installment = self.data["transaction"]["installment"] 

        """ Creating new features from the existing informations """

        self.installmentValue = self.value/self.installment

        dt = {'date':self.date, 'type':self.type, 'ant':self.antecipation, 'installment':self.installment, 'value':self.value, 'clientValue':self.clientValue, 'merchantValue':self.merchantValue, 'clientId':self.clientId, 'flatRate':self.flatRate, 'fixValue':self.fix_value, 'clientResp':self.client, 'antRate':self.antRate}

        self.transaction = pd.DataFrame(dt, index = [0])
        #self.dateLastPayment = (self.date + timedelta(days = 30*self.installment))
        #self.datePayment = self.date + timedelta(days = 1)
        #self.antValue = AntValue(self.datePayment, self.dateLastPayment, self.antRate, self.installmentValue)
    
    def MerchantPayment(self):
        split = pd.concat([self.transaction]*self.installment) if self.type == 'credit' else self.transaction
        split['installmentValue'] =  [x/y for x,y in zip(split.merchantValue, split.installment)]
        split['paymentDate'] = datePayment(self.date, self.installment, self.type)
        return split

t = transaction('dt.json')