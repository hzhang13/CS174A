from __future__ import print_function
import csv
import sys
import mysql.connector

# Fill this in with your own configuration values
config = {
  'user': 'crypto',
  'password': 'shujuku174', 
  'host': '54.183.222.108', # Localhost. If your MySQL Server is running on your own computer.
  'port': '3306', # Default port on Windows/Linux is 3306. On Mac it may be 3307.
  'database': 'project',
}

PUBLIC_KEY = "a4778d390098957740d4c69b6ba06f35"
PRIVATE_KEY = "523bc69c804c4abad05fb2290b297ce6"

try:
  cnx = mysql.connector.connect(**config)
  cursor = cnx.cursor()
except mysql.connector.Error as err:
  print("Connection Error: {}".format(err))
  sys.exit(1)

def execute(query, values):
  your_query = query % values
  print("Executing: {} ... ".format(query % values), end="")
  try:
    cursor.execute(query, values)
  except mysql.connector.Error as err:
    print("ERROR\nMySQL Error: {}\n".format(err))
    # sys.exit(1)
  else:
    print("Success")

def insert(emp_id, emp_age, emp_salary):
  """Insert a row of employee data into the database"""
  insert_employee = (
    "INSERT INTO Employees VALUES"
    "(%(id)s, %(age)s, %(salary)s)")
  enc_salary = enc(emp_salary)
  data = {'id':emp_id , 'age':emp_age, 'salary':enc_salary}
  execute(insert_employee, data)

def parse(command):
  list = command.split(" ")
  operation = list[0]
  if (operation == "INSERT") and (len(list) == 4) and (list[1].isdigit()) and (list[2].isdigit()) and (list[3].isdigit()):
    insert(list[1], list[2], list[3])
  elif operation == "SELECT":
    select(command)
  else:
    print("INPUT IS INVALID!")

def select(command):
  list = command.split(" ")
  group_by_start = command.find("GROUP BY age") 
  if list[1] == "SUM":
    if group_by_start == -1:
      prefix = "SELECT SUM_HE(salary) FROM Employees "
    else:
      prefix = "SELECT age, SUM_HE(salary) FROM Employees "
    printResult(sql_generate(prefix, command))
  elif list[1] == "AVG":
    if group_by_start == -1:
      prefix = "SELECT SUM_HE(salary), COUNT(*) FROM Employees "
    else:
      prefix = "SELECT age, SUM_HE(salary), COUNT(*) FROM Employees "
    printAVG(sql_generate(prefix, command))
  else:
    if list[1] == "*":
      sql = "SELECT * FROM Employees"
    elif list[1].isdigit():
      sql = "SELECT id, age, salary FROM Employees WHERE id = " + list[1]
    else:
      print("INPUT IS INVALID!")
      return
    printResult(sql)

def printResult(sql):
  cursor.execute(sql)
  alldata = cursor.fetchall()
  if alldata:
    for rec in alldata:
      if len(rec) == 3:
        dec_salary = dec(rec[2])
        print("(%d, %d, %s)" % (rec[0], rec[1], dec_salary))
      elif len(rec) == 2:
        dec_salary = dec(rec[1])
        print("age: %d, SUM of salary: %s" % (rec[0], dec_salary))
      else:
        dec_salary = dec(rec[0])
        if dec_salary == "0":
          dec_salary = "NULL"
        print("SUM of salary: %s" % dec_salary)
  else:
    print("The employee(s) doesn't exist")

def printAVG(sql):
  cursor.execute(sql)
  alldata = cursor.fetchall()
  if alldata:
    for rec in alldata:
      if len(rec) == 3:
        dec_sum = float(dec(rec[1]))
        avg = dec_sum/rec[2]
        print("(age: %d, AVG of salary: %f)" % (rec[0], avg))
      else:
        if rec[1] != 0:
          dec_sum = float(dec(rec[0]))
          avg = dec_sum/rec[1] 
        else:
         avg = "NULL"
        print("AVG of salary: %f" % avg)
  else:
    print("AVG of salary: NULL")

def sql_generate(sql, command):
  where_start = command.find("WHERE")
  group_by_start = command.find("GROUP BY age")
  having_start = command.find("HAVING")
  if where_start != -1:
      if group_by_start != -1:
        sql = sql + command[where_start : group_by_start]
      else:
        sql = sql + command[where_start : len(command)]
  if group_by_start != -1:
    sql += "GROUP BY age"
  if having_start != -1:
    sql = sql + " " + command[having_start : len(command)]
  return sql

def enc(salary):
  from subprocess import Popen, PIPE
  p = Popen(["./enc", salary, PUBLIC_KEY, PRIVATE_KEY], stdin = PIPE, stdout = PIPE, stderr = PIPE)
  output, err = p.communicate()
  return output

def dec(enc_salary):
  from subprocess import Popen, PIPE
  p = Popen(["./dec", enc_salary.decode('utf-8'), PUBLIC_KEY, PRIVATE_KEY], stdin = PIPE, stdout = PIPE, stderr = PIPE)
  output, err = p.communicate()
  return output


if __name__ == '__main__':

  while (True):
    command = raw_input(">>> Input: ")
    if command == "exit":
      break
    parse(command)
    # Commit data
    cnx.commit()

  cursor.close()
  cnx.close()