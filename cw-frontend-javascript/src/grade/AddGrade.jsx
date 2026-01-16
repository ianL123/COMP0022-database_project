import React from "react";
import axios from "axios";
import {
  Paper,
  Button,
  Typography,
  Select,
  MenuItem,
  TextField,
  Alert,
} from "@mui/material";
import { API_ENDPOINT } from "../config";

function AddGrade(props) {
  const [grade, setGrade] = React.useState({});
  const [students, setStudents] = React.useState([]);
  const [modules, setModules] = React.useState([]);
  const [registeredModules, setRegisteredModules] = React.useState([]);
  const [error, setError] = React.useState();
  const [noRegistrationsError, setNoRegistrationsError] = React.useState(false);

  React.useEffect(() => {
    axios
      .get(`${API_ENDPOINT}/students`)
      .then((response) => {
        setStudents(response.data);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  }, []);

  // When a student is selected, fetch their registered modules
  const fetchRegisteredModules = (studentId) => {
    axios
      .get(`${API_ENDPOINT}/students/${studentId}/registrations`)
      .then((response) => {
        const modules = response.data.map(reg => reg.module);
        setRegisteredModules(modules);
        
        // Check if student has any registrations
        if (modules.length === 0) {
          setNoRegistrationsError(true);
        } else {
          setNoRegistrationsError(false);
        }
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  };

  function request() {
    if (!grade.student_id || !grade.module_code || !grade.score) {
      setError("Please fill in all fields");
      return;
    }

    const gradeData = {
      student_id: parseInt(grade.student_id),
      module_code: grade.module_code,
      score: parseInt(grade.score)
    };

    const url = `${API_ENDPOINT}/students/${grade.student_id}/grades`;
    console.log('Sending request to:', url, 'with data:', gradeData);

    axios
      .post(url, gradeData)
      .then((response) => {
        console.log('Success:', response);
        props.update();
        setGrade({});
        setError(null);
      })
      .catch((error) => {
        console.error('Error adding grade:', error.response || error);
        if (error.response?.status === 404) {
          setError("Student or Module not found");
        } else if (error.response?.status === 409) {
          setError("Grade already exists for this student and module");
        } else if (error.response?.status === 403) {
          setError("Student is not registered for this module");
        } else {
          setError(error.response?.data?.message || "Error adding grade");
        }
      });
  }

  return (
    <Paper sx={{ padding: "30px" }}>
      <Typography variant="h5">Add Grade</Typography>
      <br />
      <br />
      <Select
        sx={{ minWidth: "300px" }}
        value={grade.student_id ?? ""}
        onChange={(e) => {
          setGrade({ ...grade, student_id: e.target.value, module_code: "" });
          fetchRegisteredModules(e.target.value);
        }}
        label="Student"
      >
        {students &&
          students.map((s) => {
            return (
              <MenuItem
                key={s.id}
                value={s.id}
              >{`${s.firstName} ${s.lastName} (${s.id})`}</MenuItem>
            );
          })}
      </Select>

      {noRegistrationsError && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          This student is not registered for any modules. 
          Please register the student to a module before adding a grade.
        </Alert>
      )}

      {!noRegistrationsError && (
        <>
          <Select
            sx={{ minWidth: "300px" }}
            value={grade.module_code ?? ""}
            onChange={(e) => setGrade({ ...grade, module_code: e.target.value })}
            label="Module"
            disabled={!grade.student_id}
          >
            {registeredModules.map((m) => {
              return (
                <MenuItem
                  key={m.code}
                  value={m.code}
                >{`${m.code} ${m.name}`}</MenuItem>
              );
            })}
          </Select>
          <TextField
            label="Score"
            value={grade.score ?? 0}
            onChange={(e) => setGrade({ ...grade, score: e.target.value })}
          />
        </>
      )}
      
      <br />
      <br />
      <Button 
        onClick={request}
        disabled={!grade.student_id || (registeredModules.length === 0) || !grade.module_code || !grade.score}
      >
        Add
      </Button>
      <br />
      <br />
      {error && <Alert color="error">{error}</Alert>}
    </Paper>
  );
}

export default AddGrade;