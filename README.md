# cp2-bucketlist
Bucket list API using Flask

## Installation
1. Clone the project - `git clone git@github.com:mungaiandela/cp2-bucketlist.git`
2. create a virtual environment using virtualenv.
3. Install the dependencies - `pip install -r requirements.txt`.
4. run the following commands to set the database ready:-
  -- `flask db init`
  -- `flask db migrate`
  -- `flask db upgrade`
The following are the API endpoints:-

| EndPoint                                  | Functionality                    |
| ------------------------------            |:-------------------------------: |
| POST /v1/auth/login                          | Logs a user in                   |
| POST /v1/auth/register                       | Register a new user              |
| POST /v1/bucketlists/                         | Create a new bucket list         |
| GET /v1/bucketlists/                         | List all bucketlists for currently logged in user|
| GET /v1/bucketlists/<id>                     | Fetches a single bucketlist      |
| PUT /v1/bucketlists/<id>                     | Update a bucketlist              |
| DELETE /v1/bucketlists/<id>                  | Delete a single bucket list      |
| POST /v1/bucketlists/<id>/items/             | Create a new bucketlist item     |
| PUT /v1/bucketlists/<id>/items/<item_id>/     | Updates a bucketlist item        |
| DELETE /v1/bucketlists/<id>/items/<item_id/>  | Deletes a bucketlist item        |

## Run the server
  5. Next is to start the server with the command `python run.py`
    The server should be running on [http://127.0.0.1:5000]

# Usage
  Use Postman (a Google chrome extension for api testing).
  Alternatively Insomnia is also a REST client.
