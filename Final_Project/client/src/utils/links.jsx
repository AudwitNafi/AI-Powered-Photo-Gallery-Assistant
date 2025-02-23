import React from "react";

import { IoBarChartSharp } from "react-icons/io5";
// import { MdQueryStats } from 'react-icons/md';
// import { FaWpforms } from 'react-icons/fa';
import { ImProfile } from "react-icons/im";
import { MdAdminPanelSettings } from "react-icons/md";
import { IoMdHome } from "react-icons/io";
import { FaDonate } from "react-icons/fa";
import { MdInventory } from "react-icons/md";
import { MdCrisisAlert } from "react-icons/md";
import { CiUser } from "react-icons/ci";

const links = [
  {
    text: "Chat",
    path: ".",
    icon: <IoMdHome />,
  },
  {
    text: "Gallery",
    path: "gallery",
    icon: <MdCrisisAlert />,
  },
  {
    text: "Upload",
    path: "inventory",
    icon: <MdInventory />,
  },

];

export default links;
