Below is the complete **frontend code** for the CRUD operations (Create, Read, Update, Delete) with a Flask backend. This example uses **React** to run the frontend, which will interact with the Flask API running on `http://localhost:5000`. The frontend will be hosted on `http://localhost:3000` (the default port for React apps).

### Full Frontend Code

1. **Setup React App** (Optional)
   If you haven't already set up the React project, follow these steps:

   - **Install Node.js** if you haven't already from [here](https://nodejs.org/).
   - **Create a new React app** by running:

   ```bash
   npx create-react-app frontend
   cd frontend
   npm start
   ```

   This will create a new React app and start the development server at `http://localhost:3000`.

2. **Frontend Code (App.js)**

   Below is the complete `App.js` file for your React frontend:

```javascript
import React, { useState, useEffect } from 'react';
import './App.css';

const apiUrl = 'http://localhost:5000'; // Flask API running on localhost:5000

function App() {
  const [users, setUsers] = useState([]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [updateId, setUpdateId] = useState('');
  const [updateName, setUpdateName] = useState('');
  const [updateEmail, setUpdateEmail] = useState('');

  // Fetch users from the Flask backend
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${apiUrl}/users`);
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Create a new user
  const createUser = async () => {
    if (!name || !email) {
      alert('Please fill in both name and email.');
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email }),
      });

      const result = await response.json();
      alert(result.message);
      setName('');
      setEmail('');
      fetchUsers(); // Refresh the user list
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  // Update an existing user
  const updateUser = async () => {
    if (!updateId || (!updateName && !updateEmail)) {
      alert('Please provide an ID and at least one field (name or email) to update.');
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/user/${updateId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: updateName, email: updateEmail }),
      });

      const result = await response.json();
      alert(result.message);
      setUpdateId('');
      setUpdateName('');
      setUpdateEmail('');
      fetchUsers(); // Refresh the user list
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  // Delete a user
  const deleteUser = async (id) => {
    try {
      const response = await fetch(`${apiUrl}/user/${id}`, {
        method: 'DELETE',
      });

      const result = await response.json();
      alert(result.message);
      fetchUsers(); // Refresh the user list
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  return (
    <div className="App">
      <h1>Flask CRUD API - React Frontend</h1>

      {/* Create User */}
      <div>
        <h3>Create User</h3>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button onClick={createUser}>Create User</button>
      </div>

      {/* Update User */}
      <div>
        <h3>Update User</h3>
        <input
          type="number"
          placeholder="User ID to Update"
          value={updateId}
          onChange={(e) => setUpdateId(e.target.value)}
        />
        <input
          type="text"
          placeholder="New Name"
          value={updateName}
          onChange={(e) => setUpdateName(e.target.value)}
        />
        <input
          type="email"
          placeholder="New Email"
          value={updateEmail}
          onChange={(e) => setUpdateEmail(e.target.value)}
        />
        <button onClick={updateUser}>Update User</button>
      </div>

      {/* Users List */}
      <div>
        <h3>Users List</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>
                  <button onClick={() => deleteUser(user.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
```

### 3. **CSS (App.css)**

You can add some simple styling for the frontend. You can modify the default `App.css` or create your own styles.

```css
.App {
  font-family: Arial, sans-serif;
  margin: 20px;
}

input {
  padding: 8px;
  margin-right: 10px;
  margin-bottom: 10px;
  width: 200px;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 8px;
  border: 1px solid #ddd;
  text-align: left;
}
```

### 4. **Instructions to Run the Frontend**

#### 1. **Ensure Flask Backend is Running:**

First, make sure your Flask backend (API) is running on `http://localhost:5000`. Here's how you can run it:

- **Install required dependencies** if not done already:

  ```bash
  pip install flask flask-cors flask-sqlalchemy
  ```

- **Run your Flask app** (ensure CORS is enabled for `http://localhost:3000` as explained earlier):

  ```bash
  python app.py
  ```

This will start your Flask backend server on `http://localhost:5000`.

#### 2. **Run the React Frontend:**

Next, you need to run the React frontend on port `3000`.

- **Navigate to the React project directory** (where `package.json` is located):

  ```bash
  cd frontend
  ```

- **Install the required dependencies** (if not done already):

  ```bash
  npm install
  ```

- **Start the React development server:**

  ```bash
  npm start
  ```

This will start the React app on `http://localhost:3000`.

#### 3. **Test the Application:**

- **Open your browser** and visit `http://localhost:3000`.
- You should see the frontend with the following sections:
  - **Create User**: Allows you to add a new user.
  - **Update User**: Allows you to update the name and/or email of an existing user by ID.
  - **Users List**: Displays a list of users with delete buttons next to each.

#### 4. **Interacting with the API:**

- **Create** a user by entering the name and email and clicking "Create User."
- **Update** an existing user by entering the user ID and the new name/email, then clicking "Update User."
- **Delete** a user by clicking the "Delete" button next to their entry in the user list.

### Conclusion:

With this setup, you have:

- **React frontend** running on `localhost:3000` to interact with the Flask backend.
- **Flask backend** running on `localhost:5000` with **CORS** enabled to allow requests from `localhost:3000`.
- **CRUD operations** to create, read, update, and delete users in the backend, all from the frontend.

This is a fully functional React application that can communicate with your Flask backend via API calls!