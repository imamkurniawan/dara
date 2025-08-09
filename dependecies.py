# pip install pandas, openpyxl, plotly

from flask import Flask, redirect, request, render_template, url_for, flash, session, jsonify, send_file
import pandas as pd
import numpy as np
# import plotly.graph_objs as go
# import plotly.io as pio
import arrow # untuk formating date
from openpyxl import load_workbook
import os
import csv
import logging
from datetime import datetime, date
import requests
# import subprocess
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import math
from io import BytesIO
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool
import hashlib
import socket