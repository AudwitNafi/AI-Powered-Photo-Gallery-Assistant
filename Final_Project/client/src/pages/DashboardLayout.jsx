import { Outlet, redirect, useLoaderData, useNavigate } from "react-router-dom";
import Wrapper from "../assets/wrappers/Dashboard";
import { BigSidebar, Navbar, SmallSidebar } from "../components";
import { createContext, useContext, useState } from "react";
import customFetch from "../utils/customFetch";
import { toast } from "react-toastify";

//global context for toggling the sidebars and user logouts
const DashboardContext = createContext();

function DashboardLayout() {
  const user = useLoaderData();

  const navigate = useNavigate();

  const [showSidebar, setShowSidebar] = useState(false);

  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
  };

  const logoutUser = async () => {
    navigate("/");
    await customFetch.get("/auth/logout");
    toast.success("Logged out...");
  };
  return (
    <DashboardContext.Provider
      value={{ user, showSidebar, toggleSidebar, logoutUser }}
    >
      <Wrapper>
        <main className="dashboard">
          <SmallSidebar />
          {/* display only one based on screen size */}
          <BigSidebar />
          <div>
            <Navbar />
            <div className="dashboard-page">
              <Outlet context={{ user }} />
            </div>
          </div>
        </main>
      </Wrapper>
    </DashboardContext.Provider>
  );
}

//creating a custom hook to avoid exporting the main context
export const useDashboardContext = () => useContext(DashboardContext);

export default DashboardLayout;
