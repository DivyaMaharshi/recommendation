from engine.models import Users
from engine.models import Books
from engine.models import UserClickHistory,UserBoughtHistory,PurchaseHistory

# import pandas
'''
import pandas as pd
from pandas import DataFrame
import calendar
import numpy as np
'''

#inbuilt library
import datetime
import time
from datetime import date,timedelta
from datetime import datetime
import json
import calendar
from django.db.models import Count
from django.db.models import Avg,Min,Max,F,Sum,Q
