import React, { useState, useEffect } from 'react';
import { Typography, Grid, Paper, Card, CardContent, Breadcrumbs, Link, Alert } from '@mui/material';
import axios from 'axios';
import { API_ENDPOINT } from '../config';
import App from '../App';

function Statistics() {
  const [averageGrades, setAverageGrades] = useState({});
  const [moduleAverages, setModuleAverages] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch average grades per student
    axios.get(`${API_ENDPOINT}/statistics/average/student`)
      .then((response) => {
        setAverageGrades(response.data);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });

    // Fetch average grades per module
    axios.get(`${API_ENDPOINT}/statistics/average/module`)
      .then((response) => {
        setModuleAverages(response.data);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  }, []);

  return (
    <App>
      <Breadcrumbs sx={{ marginBottom: "30px" }}>
        <Link underline="hover" href="/">Home</Link>
        <Typography color="text.primary">Statistics</Typography>
      </Breadcrumbs>

      {error && <Alert severity="error">{error}</Alert>}

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h4" gutterBottom align="center">
            Academic Performance Statistics
          </Typography>
        </Grid>

        {/* Average Grades Per Student */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Average Grades Per Student
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(averageGrades).map(([studentName, average]) => (
                <Grid item xs={12} sm={6} md={4} key={studentName}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" component="div">
                        {studentName}
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        Average Grade: {average !== null ? average.toFixed(2) : 'N/A'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Average Grades Per Module */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Average Grades Per Module
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(moduleAverages).map(([moduleName, average]) => (
                <Grid item xs={12} sm={6} md={4} key={moduleName}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" component="div">
                        {moduleName}
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        Average Grade: {average !== null ? average.toFixed(2) : 'N/A'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </App>
  );
}

export default Statistics; 