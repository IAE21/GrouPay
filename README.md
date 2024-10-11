# GrouPay

# Group Members:
- Ian Estevez
- William Hudmon
- Jack Throdahl

   ###
   Description:
   - GrouPay is a web application designed to facilitate users in reconciling collective debts, by allowing individuals to join billing groups, in which they can independently contribute to bills owed by themselves and their peers within the same billing group. Users must first make accounts in order to find the other users with which to join the same billing group, set up by a third party such as a landlord (or property manager, company, etc.), after which they can split bills, such as rent or utilities evenly, and/or distribute percentages of the balance due however they decide. This way, users are individually held accountable for their own parts of the total balance due, simplifying the process of collectively managing mutual expenses. 

   ###
   Problem Statement:
   - Being college students ourselves, we’ve had our fair share of roommates along the way, and have had to manage the ordeal of paying bills through other people, or doing it ourselves for things like common appliances and shared goods, which is not always a pleasant experience. Considering most college dorm mates or roommates are strangers, it is difficult and often uncomfortable to hold others accountable for such expenses. However, this project will make it concretely evident who is not pulling their weight, simplifying the conversation for all those involved.

   ###
   How to compile & run project:
   - In the project's directory, using the command line, run
   ```bash
   python3 app.py
   ```
   
   ###
   Division of Labour:
   ###
   Front End: Jack Throdahl, Ian Estevez

   ###
   Back End: William Hudmon, Ian Estevez

   ###
   Important Dependencies:
   MySQL Server, Werkzeug 2.2.2, Flask 2.2.2, flask-msqldb, python3

   ###
   Other Instructions:
   If running the project in Ubuntu, it may be necessary to manually open the MySQL server from the command line to edit the authentication_plugin attribute of the user 'root' to change it to 'caching_sha2_password' instead of 'auth_socket' or 'mysql_native_password'.
   This can be done by opening the msyql server in the commandline:
      ```bash
   sudo mysql -u root
   ```
   Then, once in the mysql server command prompt, run the command:
      ```bash
   ALTER USER 'root'@'localhost' IDENTIFIED WITH 'caching_sha2_password' BY 'mysql123';
   ```
