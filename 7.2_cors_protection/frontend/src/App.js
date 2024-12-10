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