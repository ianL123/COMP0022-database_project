import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import { Container } from "@mui/material";

function App(props) {
  return <Container>{props.children}</Container>;
}

export default App;
