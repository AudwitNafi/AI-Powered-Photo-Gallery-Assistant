// import styled from "styled-components";
import Wrapper from "../assets/wrappers/LandingPage";
import main from "../assets/images/landing-page.jpg";
import { Link } from "react-router-dom";
import { Logo } from "../components";

function Landing() {
  return (
    <Wrapper>
      <nav>
        <Logo />
      </nav>
      <div className="container page">
        <div className="info">
          <h1>
            Disaster <span>Management</span> Application
          </h1>
          <p>
            Welcome to the Disaster Management System, a comprehensive platform
            dedicated to enhancing disaster response and relief efforts. Our
            mission is to connect communities, volunteers, donors, and
            administrators to work collaboratively in managing crises
            efficiently and effectively.
          </p>
          <Link className="btn register-link" to="/register">
            Register
          </Link>
          <Link className="btn" to="/login">
            Login
          </Link>
        </div>
        <img src={main} alt="main" className="img main-img" />
      </div>
    </Wrapper>
  );
}

export default Landing;
