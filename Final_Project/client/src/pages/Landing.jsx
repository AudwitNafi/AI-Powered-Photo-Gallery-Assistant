// import styled from "styled-components";
import Wrapper from "../assets/wrappers/LandingPage";
import main from "../assets/images/meilleur-chatbot.jpg";
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
            Conversational <span>Memory</span> Bot
          </h1>
          <p>
            Welcome to the Conversational Memory Bot, an AI-powered photo gallery assistant.  This is an AI-powered chatbot, designed to revolutionize the
           way users interact with their personal photo galleries. By combining advanced Natural
           Language Processing (NLP) and other frameworks, this system enables users to query,
           retrieve, and explore their photos using natural language and visual features.
          </p>
          <Link className="btn" to="/dashboard">
            Get Started
          </Link>
        </div>
        <img src={main} alt="main" className="img main-img" />
      </div>
    </Wrapper>
  );
}

export default Landing;
