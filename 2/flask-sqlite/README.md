# Rest API with flask and sqlite3
  The flask framework is used with sqlite3 database to create rest api. Restful api is built wtih json data for a client.microservice.

# Authorization credentials
*  username = shreyaskn72
*  Password = secret

# Methods used
*  GET
*  POST
*  DELETE
*  PUT
   
# Endpoints
*  http://127.0.0.1:8080/product
*  http://127.0.0.1:8080/product/<id>
*  http://127.0.0.1:8080/product/update
*  http://127.0.0.1:8080/product/delete
  
# Requests and Responses example

* Adding a product using POST method

* Endpoint used: http://127.0.0.1:8080/product

* Method used: POST

* Request

{   
    "name": "colgate",
    "description": "This is for brushing teeth",
    "price": 40,
    "qty": 2
}


* Response

{
    "1": {
        "description": "This is for brushing teeth",
        "name": "colgate",
        "price": 40,
        "qty": 2
    }
}


