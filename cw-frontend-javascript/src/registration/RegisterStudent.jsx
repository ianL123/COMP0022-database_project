import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Breadcrumbs,
  Link,
  Typography,
  Alert,
  Grid,
  Paper,
  Button,
  Autocomplete,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { API_ENDPOINT } from "../config";
import App from "../App";

function RegisterStudent() {
  const [students, setStudents] = useState([]);
  const [modules, setModules] = useState([]);
  const [registration, setRegistration] = useState({
    studentId: null,
    moduleCode: "",
  });
  const [error, setError] = useState(null);
  const [registrationsList, setRegistrationsList] = useState([]);

  useEffect(() => {
    // Fetch students and modules on component mount
    axios.get(`${API_ENDPOINT}/students`)
      .then((response) => {
        setStudents(response.data);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });

    axios.get(`${API_ENDPOINT}/modules`)
      .then((response) => {
        const moduleList = response.data._embedded 
          ? response.data._embedded.modules 
          : response.data;
        
        setModules(moduleList);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });

    // Fetch the list of registrations on component mount
    axios.get(`${API_ENDPOINT}/registrations`)
      .then((response) => {
        setRegistrationsList(response.data);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  }, []);

  const handleRegister = async () => {
    if (!registration.studentId || !registration.moduleCode) {
      setError("Please select a student and a module.");
      return;
    }

    try {
      const response = await axios.post(`${API_ENDPOINT}/registrations`, {
        studentId: registration.studentId,
        moduleCode: registration.moduleCode,
      });

      if (response.status === 201) {
        // Fetch the updated list of registrations
        const registrationsResponse = await axios.get(`${API_ENDPOINT}/registrations`);
        setRegistrationsList(registrationsResponse.data);
      } else {
        setError("Failed to register student to module.");
      }

      setError(null);
      setRegistration({ studentId: null, moduleCode: "" });
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setError(error.response.data);
      } else {
        setError(error.response?.data?.message || error.message);
      }
    }
  };

  return (
    <App>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link underline="hover" color="inherit" href="/">
              Home
            </Link>
            <Typography color="text.primary">Register Student</Typography>
          </Breadcrumbs>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h5" gutterBottom>
              Register Student to Module
            </Typography>

            {error && (
              <Alert severity="error" sx={{ marginBottom: 2 }}>
                {error}
              </Alert>
            )}

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Autocomplete
                  options={students}
                  getOptionLabel={(student) => 
                    `${student.firstName} ${student.lastName} (ID: ${student.id})`
                  }
                  value={
                    students.find(student => student.id === registration.studentId) || null
                  }
                  onChange={(event, newValue) => {
                    setRegistration({ 
                      ...registration, 
                      studentId: newValue ? newValue.id : null 
                    });
                  }}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      label="Student" 
                      variant="outlined" 
                      fullWidth 
                    />
                  )}
                  filterOptions={(options, { inputValue }) => 
                    options.filter(
                      (student) => 
                        student.firstName.toLowerCase().includes(inputValue.toLowerCase()) ||
                        student.lastName.toLowerCase().includes(inputValue.toLowerCase()) ||
                        student.id.toString().includes(inputValue)
                    )
                  }
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Autocomplete
                  options={modules}
                  getOptionLabel={(module) => `${module.code} - ${module.name}`}
                  value={
                    modules.find(module => module.code === registration.moduleCode) || null
                  }
                  onChange={(event, newValue) => {
                    setRegistration({ 
                      ...registration, 
                      moduleCode: newValue ? newValue.code : '' 
                    });
                  }}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      label="Module" 
                      variant="outlined" 
                      fullWidth 
                    />
                  )}
                  filterOptions={(options, { inputValue }) => 
                    options.filter(
                      (module) => 
                        module.code.toLowerCase().includes(inputValue.toLowerCase()) ||
                        module.name.toLowerCase().includes(inputValue.toLowerCase())
                    )
                  }
                />
              </Grid>

              <Grid item xs={12}>
                <Button 
                  variant="contained" 
                  onClick={handleRegister}
                  disabled={!registration.studentId || !registration.moduleCode}
                >
                  Register
                </Button>
              </Grid>
            </Grid>

  {registrationsList.length > 0 && (
    <TableContainer component={Paper} sx={{ marginTop: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>ID</TableCell>
            <TableCell>Username</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Modules</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {registrationsList.reduce((acc, registration) => {
            const existingStudent = acc.find(
              (student) => student.id === registration.student.id
            );
            if (existingStudent) {
              existingStudent.modules.push(registration.module);
            } else {
              acc.push({
                id: registration.student.id,
                firstName: registration.student.firstName,
                lastName: registration.student.lastName,
                username: registration.student.username,
                email: registration.student.email,
                modules: [registration.module],
              });
            }
            return acc;
          }, []).map((student) => (
            <TableRow key={student.id}>
              <TableCell>
                {student.firstName} {student.lastName}
              </TableCell>
              <TableCell>{student.id}</TableCell>
              <TableCell>{student.username}</TableCell>
              <TableCell>{student.email}</TableCell>
              <TableCell>
                {student.modules.map((module) => (
                  <div key={module.code}>
                    {module.code} - {module.name}
                  </div>
                ))}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )}
          </Paper>
        </Grid>
      </Grid>
    </App>
  );
}

export default RegisterStudent;