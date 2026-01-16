import React from "react";
import axios from "axios";
import { 
  Breadcrumbs, 
  Link, 
  Typography, 
  Alert, 
  Grid, 
  Button, 
  Dialog, 
  DialogActions, 
  DialogContent, 
  DialogTitle, 
  TextField,
  InputAdornment
} from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import App from "../App";
import { API_ENDPOINT } from "../config";
import AddGrade from "./AddGrade";

function GradeRow(props) {
  const { grade, onEdit, onDelete } = props;
  const [student, setStudent] = React.useState();
  const [module, setModule] = React.useState();
  const [editDialogOpen, setEditDialogOpen] = React.useState(false);
  const [newScore, setNewScore] = React.useState(grade.score);

  React.useEffect(() => {
    axios
      .get(grade._links.module.href)
      .then((response) => setModule(response.data));

    axios
      .get(grade._links.student.href)
      .then((response) => setStudent(response.data));
  }, [grade]);

  const handleEdit = () => {
    axios
      .put(`${API_ENDPOINT}/grades/${grade.id}`, { score: newScore })
      .then(() => {
        onEdit();
        setEditDialogOpen(false);
      });
  };

  const handleDelete = () => {
    axios
      .delete(`${API_ENDPOINT}/grades/${grade.id}`)
      .then(() => {
        onDelete();
      });
  };

  return (
    <Grid key={grade.id} container style={{ padding: "10px 0" }}>
      <Grid item xs={4}>
        {student && `${student.firstName} ${student.lastName} (${student.id})`}
      </Grid>
      <Grid item xs={4}>
        {module && `${module.code} ${module.name}`}
      </Grid>
      <Grid item xs={4}>
        {grade.score}
        <Button onClick={() => setEditDialogOpen(true)}>Edit</Button>
        <Button onClick={handleDelete}>Delete</Button>
      </Grid>

      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>Edit Grade</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Score"
            type="number"
            fullWidth
            value={newScore}
            onChange={(e) => setNewScore(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleEdit}>Save</Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
}

function Grades() {
  const [grades, setGrades] = React.useState([]);
  const [filteredGrades, setFilteredGrades] = React.useState([]);
  const [error, setError] = React.useState();
  const [searchTerm, setSearchTerm] = React.useState("");

  React.useEffect(() => {
    updateGrades();
  }, []);

  React.useEffect(() => {
    // Filter grades based on search term
    const filtered = grades.filter(grade => {
      if (!searchTerm) return true;
  
      const searchLower = searchTerm.toLowerCase();
  
      const studentMatch = 
        (grade.student && (
          grade.student.firstName.toLowerCase().startsWith(searchLower) ||
          grade.student.lastName.toLowerCase().startsWith(searchLower) ||
          grade.student.id.toString().startsWith(searchLower)
        ));
  
      const moduleMatch = 
        (grade.module && (
          grade.module.code.toLowerCase().startsWith(searchLower) ||
          grade.module.name.toLowerCase().startsWith(searchLower)
        ));
  
      const scoreMatch = grade.score.toString().startsWith(searchLower);
      
      return studentMatch || moduleMatch || scoreMatch;
    });
    
    setFilteredGrades(filtered);
  }, [searchTerm, grades]);

  function updateGrades() {
    axios
      .get(`${API_ENDPOINT}/grades`)
      .then((response) => {
        const gradeList = response.data._embedded.grades;
        
        const detailedGradePromises = gradeList.map(grade => 
          Promise.all([
            axios.get(grade._links.student.href),
            axios.get(grade._links.module.href)
          ]).then(([studentResponse, moduleResponse]) => ({
            ...grade,
            student: studentResponse.data,
            module: moduleResponse.data
          }))
        );
  
        return Promise.all(detailedGradePromises);
      })
      .then(detailedGrades => {
        setGrades(detailedGrades);
        setFilteredGrades(detailedGrades);
      })
      .catch((error) => {
        setError(error.response?.data?.message || error.message);
      });
  }

  return (
    <App>
      <Breadcrumbs sx={{ marginBottom: "30px" }}>
        <Link underline="hover" color="inherit" href="/">
          Home
        </Link>
        <Typography sx={{ color: "text.primary" }}>Grades</Typography>
      </Breadcrumbs>

      {/* Search Input */}
      <TextField
        fullWidth
        variant="outlined"
        label="Search Grades"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        placeholder="Search by student, module, or score"
        sx={{ marginBottom: "20px" }}
      />

      {error && <Alert color="error">{error}</Alert>}
      {!error && filteredGrades.length < 1 && <Alert color="warning">No grades</Alert>}
      
      {filteredGrades.length > 0 && (
        <>
          <Grid container style={{ padding: "10px 0" }}>
            <Grid item xs={4}>
              <Typography variant="h6">Student</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="h6">Module</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="h6">Score</Typography>
            </Grid>
          </Grid>
          {filteredGrades.map((g) => {
            return <GradeRow key={g.id} grade={g} onEdit={updateGrades} onDelete={updateGrades} />;
          })}
        </>
      )}
      <br />
      <br />
      <AddGrade update={updateGrades} />
    </App>
  );
}

export default Grades;