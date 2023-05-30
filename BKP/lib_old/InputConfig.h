#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
#include <cstdio>

int IntInput(string input = "config_file.txt", string key = "TEST")
{
  fstream newfile;
  int int_num = 0;
  newfile.open(input,ios::in); //open a file to perform read operation using file object
  if (newfile.is_open())
  {   //checking whether the file is open
    string tp;

    while(getline(newfile, tp))
    { //read data from file object and put it into string.
      if (tp.rfind(key, 0) == 0)
      { // pos=0 limits the search to the prefix
        istringstream stream(tp);
        string s;
        stream >> s >> int_num;// s starts with prefix
        //cout << run << "\n";
        //cout << tp << "\n"; //print the data of the string
      }   
    }    
    newfile.close(); //close the file object.
  }
  return int_num;
}

double DoubleInput(string input = "config_file.txt", string key = "TEST")
{
  fstream newfile;
  double double_num = 0;
  newfile.open(input,ios::in); //open a file to perform read operation using file object
  if (newfile.is_open())
  {   //checking whether the file is open
    string tp;

    while(getline(newfile, tp))
    { //read data from file object and put it into string.
      if (tp.rfind(key, 0) == 0)
      { // pos=0 limits the search to the prefix
        istringstream stream(tp);
        string s;
        stream >> s >> double_num;// s starts with prefix
        //cout << run << "\n";
        //cout << tp << "\n"; //print the data of the string
      }   
    }    
    newfile.close(); //close the file object.
  }
  return double_num;
}

string StringInput(string input = "config_file.txt",  string key = "TEST")
{
  fstream newfile;
  string string_text;
  newfile.open(input,ios::in); //open a file to perform read operation using file object
  if (newfile.is_open())
  {   //checking whether the file is open
    string tp;
    while(getline(newfile, tp))
    { //read data from file object and put it into string.
      if (tp.rfind(key, 0) == 0)
      { // pos=0 limits the search to the prefix
        istringstream stream(tp);
        string s;
        stream >> s >> string_text;// s starts with prefix
      }   
    }    
    newfile.close(); //close the file object.
  }
  return string_text;
}

bool BoolInput(string input = "config_file.txt", string key = "TEST")
{
  fstream newfile;
  string bool_condition;
  bool b = false;
  newfile.open(input,ios::in); //open a file to perform read operation using file object
  if (newfile.is_open())
  {   //checking whether the file is open
    string tp;

    while(getline(newfile, tp))
    { //read data from file object and put it into string.
      if (tp.rfind(key, 0) == 0)
      { // pos=0 limits the search to the prefix
        istringstream stream(tp);
        string s;
        stream >> s >> bool_condition; // s starts with prefix
        if (bool_condition == "1"){b = true;}
        cout << "active function: " << b << "\n";
        //cout << tp << "\n"; //print the data of the string
      }   
    }    
    newfile.close(); //close the file object.
  }
  return b;
}

std::vector<int> IntVectorInput(string input = "config_file.txt",  string key = "TEST")
{
  fstream newfile;
  std::vector<int> int_vector;
  newfile.open(input,ios::in); //open a file to perform read operation using file object
  if (newfile.is_open())
  {   //checking whether the file is open
    string tp;
    while(getline(newfile, tp))
    { //read data from file object and put it into string.
      if (tp.rfind(key, 0) == 0)
      { // pos=0 limits the search to the prefix
        istringstream stream(tp);
        string s;
        while(stream >> s) 
        {
          if(s=="CHANNEL") continue; // skip key string
          int_vector.push_back(std::stoi(s)); // convert string into int
        }
      }
    }
    newfile.close(); //close the file object.
  }
  // for (int n:int_vector) cout << "Vector element:" << n << endl; // check vector elements
  return int_vector;
}

std::vector<double> DoubleVectorInput(string input = "config_file.txt",  string key = "TEST")
{
  fstream newfile;
  std::vector<double> double_vector;
  newfile.open(input,ios::in); //open a file to perform read operation using file object
  if (newfile.is_open())
  {   //checking whether the file is open
    string tp;
    while(getline(newfile, tp))
    { //read data from file object and put it into string.
      if (tp.rfind(key, 0) == 0)
      { // pos=0 limits the search to the prefix
        istringstream stream(tp);
        string s;
        while(stream >> s) 
        {
          if(s=="PRO_VALUES") continue; // skip key string
          double_vector.push_back(std::stod(s)); // convert string into int
        }
      }
    }
    newfile.close(); //close the file object.
  }
  for (double n:double_vector) cout << "Vector element:" << n << endl; // check vector elements
  return double_vector;
}