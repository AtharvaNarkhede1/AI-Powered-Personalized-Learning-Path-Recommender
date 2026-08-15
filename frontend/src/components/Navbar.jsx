import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="brand">Career PathFinder</NavLink>
      <NavLink to="/chat">Chat</NavLink>
      <NavLink to="/path">Learning Path</NavLink>
      <NavLink to="/dashboard">Dashboard</NavLink>
    </nav>
  );
}
