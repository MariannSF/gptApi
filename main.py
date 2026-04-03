
import moviesDB


def main():

    print("loading to SQLite")
    moviesDB.load_to_sqlite()

    #prints table names
    print("Check Data")
    moviesDB.check_data()


    print("Query being Sent")
   # user_input ="Show me top movies after 2000, organize data so that higher rating shown first"
   # query = generate_sql(user_input)
    print("Generated SQL:++++++++++++++++++++++++++++++++++++++++++++++++++++")
   # print( query)
  #  results = moviesDB.run_query(query)

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
  #  for (title) in results:
  #     print(title)




if __name__ == '__main__':
    main()

