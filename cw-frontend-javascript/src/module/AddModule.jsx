import React from "react";
import axios from "axios";
import {
  Paper,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Typography,
  Alert,
} from "@mui/material";
import { API_ENDPOINT } from "../config";

function AddModule(props) {
  const [module, setModule] = React.useState({});
  const [error, setError] = React.useState();

  function request() {
    // Validate required fields
    if (!module.code || !module.name) {
      setError("Please fill in all required fields");
      return;
    }

    axios
      .post(`${API_ENDPOINT}/modules`, module)
      .then(() => {
        props.update();
        // Clear input fields after successful addition
        setModule({});
      })
      .catch((response) => {
        setError(response.message);
      });
  }

  return (
    <Paper sx={{ padding: "30px" }}>
      <Typography variant="h5">Add/Update Module</Typography>
      <br />
      <TextField
        label="Module Code"
        value={module.code || ''}
        onChange={(e) => {
          setModule({ ...module, code: e.target.value.toUpperCase() });
        }}
      />
      <TextField
        label="Module Name"
        value={module.name || ''}
        onChange={(e) => {
          setModule({ ...module, name: e.target.value });
        }}
      />
      <br />
      <FormControlLabel
        control={
          <Switch
            checked={module.mnc ?? false}
            id="is_mnc"
            onChange={(e) => {
              setModule({ ...module, mnc: e.target.checked });
            }}
          />
        }
        label="MNC?"
      />
      <br />
      <Button 
        onClick={request}
        disabled={!module.code || !module.name} // Disable if fields are empty
      >
        Add/Update
      </Button>
      <br />
      <br />
      {error && <Alert color="error">{error}</Alert>}
    </Paper>
  );
}

export default AddModule;
