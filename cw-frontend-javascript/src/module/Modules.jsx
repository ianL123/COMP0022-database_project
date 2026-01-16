import React from "react";
import axios from "axios";
import {
  Breadcrumbs,
  Link,
  Typography,
  Alert,
  Grid,
  TextField,
  InputAdornment,
  Paper,
  Button // Importing Button from Material-UI
} from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import App from "../App.jsx";
import { API_ENDPOINT } from "../config";
import AddModule from "./AddModule";

function Modules() {
  const [modules, setModules] = React.useState([]);
  const [filteredModules, setFilteredModules] = React.useState([]);
  const [error, setError] = React.useState();
  const [searchTerm, setSearchTerm] = React.useState("");

  React.useEffect(() => {
    updateModules();
  }, []);

  React.useEffect(() => {
    // Ensure modules is always an array before filtering
    const moduleList = Array.isArray(modules) 
      ? modules 
      : (modules._embedded?.modules || modules.data || []);

    // Filter modules based on search term
    const filtered = moduleList.filter(module => 
      module.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      module.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredModules(filtered);
  }, [searchTerm, modules]);

  function handleDelete(code) {
    // Confirm deletion with the user
    if (window.confirm("Are you sure you want to delete this module?")) {
      axios
        .delete(`${API_ENDPOINT}/modules/${code}`)
        .then(() => {
          updateModules(); // Refresh the module list
        })
        .catch((error) => {
          setError(error.response?.data?.message || error.message);
        });
    }
  }

  function updateModules() {
    axios
      .get(`${API_ENDPOINT}/modules`)
      .then((response) => {
        // Handle different possible response structures
        const moduleList = response.data._embedded?.modules 
          || response.data.data 
          || response.data 
          || [];

        setModules(moduleList);
        setFilteredModules(moduleList);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });

  }

  return (
    <App>
      <Breadcrumbs sx={{ marginBottom: "30px" }}>
        <Link underline="hover" href="/">Home</Link>
        <Typography color="text.primary">Modules</Typography>
      </Breadcrumbs>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <AddModule update={updateModules} />
        </Grid>

        {/* Search Input */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            variant="outlined"
            label="Search Modules"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            placeholder="Search by code or name"
          />
        </Grid>

        {error && <Alert severity="error">{error}</Alert>}

        {/* Modules List */}
        <Grid item xs={12}>
          <Typography variant="h4" gutterBottom align="center">Module List</Typography>
          <Grid container spacing={2}>
            {filteredModules.length > 0 ? (
              filteredModules.map((module) => (
                <Grid item xs={12} sm={6} md={4} key={module.code}>
                  <Paper elevation={3} sx={{ padding: 2, borderRadius: 2 }}>
                    <Typography variant="h5" component="div" color="primary">
                      {module.code} - {module.name}
                    </Typography>
                    <Typography color="text.secondary">
                      <strong>MNC:</strong> {module.mnc ? 'Yes' : 'No'}
                    </Typography>
                    <Button
                      variant="outlined" // Change to outlined for a nicer look
                      color="error" // Use error color for delete action
                      onClick={() => handleDelete(module.code)}
                      sx={{ marginTop: 1 }} // Add some margin for better spacing
                    >
                      Delete Module
                    </Button>
                  </Paper>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Typography variant="h6" align="center">No modules found.</Typography>
              </Grid>
            )}
          </Grid>
        </Grid>
      </Grid>
    </App>
  );
}

export default Modules;