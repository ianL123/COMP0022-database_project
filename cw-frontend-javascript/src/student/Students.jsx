import React, { useState } from "react";
import axios from "axios";
import {
  Breadcrumbs,
  Link,
  Typography,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  InputAdornment,
} from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import App from "../App";
import { API_ENDPOINT } from "../config";
import AddStudent from "./AddStudent";

function Students() {
  const [students, setStudents] = useState(() => {
    // Load students from local storage if available
    const savedStudents = localStorage.getItem('students');
    return savedStudents ? JSON.parse(savedStudents) : [];
  });
  const [filteredStudents, setFilteredStudents] = useState(students);
  const [error, setError] = useState();
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [currentStudent, setCurrentStudent] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  React.useEffect(() => {
    updateStudents();
  }, []);

  React.useEffect(() => {
    // Filter students based on search term
    const filtered = students.filter(student => 
      student.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.id.toString().includes(searchTerm) ||
      student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.username.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredStudents(filtered);
  }, [searchTerm, students]);

  function updateStudents() {
    axios
      .get(`${API_ENDPOINT}/students`)
      .then((response) => {
        setStudents(response.data);
        setFilteredStudents(response.data);
        // Save students to local storage
        localStorage.setItem('students', JSON.stringify(response.data));
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  }

  const handleEditClick = (student) => {
    setCurrentStudent(student);
    setEditDialogOpen(true);
  };

  const handleDeleteClick = (id) => {
    axios
      .delete(`${API_ENDPOINT}/students/${id}`)
      .then(() => {
        updateStudents();
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  };

  const handleEditSubmit = () => {
    axios
      .put(`${API_ENDPOINT}/students/${currentStudent.id}`, currentStudent)
      .then(() => {
        setEditDialogOpen(false);
        updateStudents();
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  };

  return (
    <App>
      <Breadcrumbs sx={{ marginBottom: "30px" }}>
        <Link underline="hover" href="/">Home</Link>
        <Typography color="text.primary">Students</Typography>
      </Breadcrumbs>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <AddStudent update={updateStudents} />
        </Grid>

        {/* Search Input */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            variant="outlined"
            label="Search Students"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            placeholder="Search by name, ID, email, or username"
          />
        </Grid>

        {error && <Alert severity="error">{error}</Alert>}
        
        {/* Students List */}
        <Grid item xs={12}>
          <Typography variant="h4" gutterBottom align="center">Student List</Typography>
          <Grid container spacing={2}>
            {filteredStudents.length > 0 ? (
              filteredStudents.map((student) => (
                <Grid item xs={12} sm={6} md={4} key={student.id}>
                  <Paper elevation={3} sx={{ padding: 2, borderRadius: 2 }}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h5" component="div" color="primary">
                          {`${student.firstName} ${student.lastName}`}
                        </Typography>
                        <Typography color="text.secondary">
                          <strong>ID:</strong> {student.id}
                        </Typography>
                        <Typography color="text.secondary">
                          <strong>Username:</strong> {student.username}
                        </Typography>
                        <Typography color="text.secondary">
                          <strong>Email:</strong> {student.email}
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <Button size="small" color="primary" onClick={() => handleEditClick(student)}>Edit</Button>
                        <Button size="small" color="secondary" onClick={() => handleDeleteClick(student.id)}>Delete</Button>
                      </CardActions>
                    </Card>
                  </Paper>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Typography variant="h6" align="center">No students found.</Typography>
              </Grid>
            )}
          </Grid>
        </Grid>
      </Grid>

      {/* Edit Student Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>Edit Student</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="First Name"
            type="text"
            fullWidth
            variant="outlined"
            value={currentStudent?.firstName || ''}
            onChange={(e) => setCurrentStudent({ ...currentStudent, firstName: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Last Name"
            type="text"
            fullWidth
            variant="outlined"
            value={currentStudent?.lastName || ''}
            onChange={(e) => setCurrentStudent({ ...currentStudent, lastName: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Username"
            type="text"
            fullWidth
            variant="outlined"
            value={currentStudent?.username || ''}
            onChange={(e) => setCurrentStudent({ ...currentStudent, username: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Email"
            type="email"
            fullWidth
            variant="outlined"
            value={currentStudent?.email || ''}
            onChange={(e) => setCurrentStudent({ ...currentStudent, email: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)} color="primary">Cancel</Button>
          <Button onClick={handleEditSubmit} color="primary">Save</Button>
        </DialogActions>
      </Dialog>
    </App>
  );
}

export default Students;
