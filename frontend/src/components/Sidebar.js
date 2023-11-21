import { Link, NavLink } from "react-router-dom";
import {
  ProSidebar,
  Menu,
  MenuItem,
  SubMenu,
  SidebarHeader,
  SidebarFooter,
  SidebarContent,
} from "react-pro-sidebar";
import {
  FaUser,
  FaAngleDoubleLeft,
  FaAngleDoubleRight,
  FaThList,
  FaNetworkWired,
  FaRegCommentAlt,
  FaUserCog,
  FaUserInjured,
} from "react-icons/fa";
import Button from "@mui/material/Button";
const Sidebar = ({
  image,
  collapsed,
  toggled,
  handleToggleSidebar,
  handleCollapsedChange,
}) => {
  return (
    <ProSidebar
      collapsed={collapsed}
      toggled={toggled}
      onToggle={handleToggleSidebar}
      breakPoint="md"
    >
      {/* Header */}
      <SidebarHeader>
        <Menu iconShape="circle">
          {collapsed ? (
            <MenuItem
              icon={<FaAngleDoubleRight />}
              onClick={handleCollapsedChange}
            ></MenuItem>
          ) : (
            <MenuItem
              suffix={<FaAngleDoubleLeft />}
              onClick={handleCollapsedChange}
            ></MenuItem>
          )}
        </Menu>
      </SidebarHeader>
      {/* Content */}
      <SidebarContent>
        {/* <Menu iconShape="none">
          <MenuItem icon={<FaThList />}>
            Dashboard
            <NavLink to="/" />
          </MenuItem>

          <SubMenu title={"CHW"} icon={<FaUserCog />}>
            <MenuItem>CHW Account</MenuItem>
            <MenuItem>CHW Group</MenuItem>
          </SubMenu>
          <SubMenu title={"Client"} icon={<FaUserInjured />}>
            <MenuItem>Client Account</MenuItem>
            <MenuItem>Client Group</MenuItem>
          </SubMenu>
          <MenuItem icon={<FaNetworkWired />}>
            Pathway <Link to="/pathway" />
          </MenuItem>
          <SubMenu title={"Audit/Log"} icon={<FaRegCommentAlt />}>
            <MenuItem>CHW Log </MenuItem>
            <MenuItem>Client Log </MenuItem>
            <MenuItem>Pathway Log </MenuItem>
          </SubMenu>
        </Menu> */}
      </SidebarContent>
      {/* Footer */}
      <SidebarFooter style={{ textAlign: "center" }}>
        <div className="sidebar-btn-wrapper" style={{ padding: "16px" }}>
          <Link
            iconShape="none"
            className="sidebar-btn"
            style={{ cursor: "pointer" }}
            to="/login"
          >
            <FaUser />
            <span>My Account</span>
          </Link>
        </div>
      </SidebarFooter>
    </ProSidebar>
  );
};

export default Sidebar;
