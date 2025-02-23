import { toast } from "react-toastify";
import Wrapper from "../assets/wrappers/Home";
import { Link, useLoaderData, useOutletContext } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import ChatInterface from "../components/ChatInterface.jsx";


function Dashboard() {
  const navigate = useNavigate();
  return (
    <Wrapper>
      <ChatInterface/>
    </Wrapper>
  );
}
export default Dashboard;
