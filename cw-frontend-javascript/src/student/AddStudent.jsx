import React from "react";
import axios from "axios";
import { Paper, TextField, Button, Typography, Alert } from "@mui/material";
import { API_ENDPOINT } from "../config";

function AddStudent(props) {
  const [student, setStudent] = React.useState({
    id: '',
    firstName: '',
    lastName: '',
    username: '',
    email: ''
  });
  const [error, setError] = React.useState();

  function request() {
    // Validate required fields
    if (!student.id || !student.firstName || !student.lastName || !student.username || !student.email) {
      setError("Please fill in all required fields");
      return;
    }

    // Ensure ID is a number
    const studentId = Number(student.id);
    if (isNaN(studentId)) {
      setError("ID must be a valid number");
      return;
    }

    // Validate email
    if (!student.email.includes('@')) {
      setError("Must enter a valid email");
      return;
    }

    const studentData = {
      ...student,
      id: studentId  // Use the validated number
    };

    axios
      .post(`${API_ENDPOINT}/students`, studentData)
      .then(() => {
        props.update();
        // Clear form after successful submission
        setStudent({
          id: '',
          firstName: '',
          lastName: '',
          username: '',
          email: ''
        });
        setError(null);
      })
      .catch((error) => {
        const errorMessage = error.response?.data?.message || error.message;
        setError(`Failed to add student: ${errorMessage}`);
      });
  }

  return (
    <Paper sx={{ padding: "30px" }}>
      <Typography variant="h5">Add/Update Student</Typography>
      <br />
      <TextField
        label="ID"
        value={student.id}
        onChange={(e) => setStudent({ ...student, id: e.target.value })}
      />
      <TextField
        label="First Name"
        value={student.firstName}
        onChange={(e) => setStudent({ ...student, firstName: e.target.value })}
      />
      <TextField
        label="Last Name"
        value={student.lastName}
        onChange={(e) => setStudent({ ...student, lastName: e.target.value })}
      />
      <TextField
        label="Username"
        value={student.username}
        onChange={(e) => setStudent({ ...student, username: e.target.value })}
      />
      <TextField
        label="Email"
        value={student.email}
        onChange={(e) => setStudent({ ...student, email: e.target.value })}
      />
      <br />
      <Button 
        variant="contained" 
        onClick={request}
        disabled={!student.id || !student.firstName || !student.lastName || !student.username || !student.email}
      >
        Add/Update
      </Button>
      <br />
      <br />
      {error && <Alert severity="error">{error}</Alert>}
    </Paper>
  );
}

export default AddStudent;
