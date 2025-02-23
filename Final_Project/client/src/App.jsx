import { createBrowserRouter, RouterProvider } from "react-router-dom";
import {
  Landing,
  Gallery,
  Dashboard,
  DashboardLayout,
  HomeLayout,
  BatchUploadPage,
  ImageDetailPage,
} from "./pages";
const router = createBrowserRouter([
  {
    path: "/",
    element: <HomeLayout />,
    children: [
      {
        index: true,
        element: <Landing />,
      },
      {
        path: "dashboard",
        element: <DashboardLayout />,

        children: [
          {
            index: true,
            element: <Dashboard />,
          },
          {
            path: "inventory",
            element: <BatchUploadPage />,
          },
          {
            path: "gallery",
            element: <Gallery />,
          },
          {
            path : "gallery/:id",
            element :<ImageDetailPage />
          },
        ],
      },
    ],
  },
]);

const App = () => {
  return <RouterProvider router={router} />;
};

export default App;
