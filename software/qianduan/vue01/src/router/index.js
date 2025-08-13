// src/router.js
import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/login.vue"; // 登录组件
import Register from "../views/register.vue"; // 注册组件
import ForgotPwd from "../views/ForgotPwd.vue"; // 忘记密码组件
import register_Mail from "../views/register_Mail.vue";
import ForgotPwd_reset from "../views/ForgotPwd_reset.vue";
import homepage from "../views/Homepage.vue";

const routes = [
  {
    path: "/",
    name: "login",
    component: Login,
  },
  {
    path: "/register",
    name: "register",
    component: Register,
  },
  {
    path: "/forgot-password",
    name: "ForgotPwd",
    component: ForgotPwd,
  },
  {
    path: "/register_Mail",
    name: "register_Mail",
    component: register_Mail,
  },
  {
    path: "/ForgotPwd_reset",
    name: "ForgotPwd_reset",
    component: ForgotPwd_reset,
  },
  {
    path: "/homepage",
    name: "homepage",
    component: homepage,
  },
   {
    path: "/AItrainingplan",
    name: "AItrainingplan",
    component: () => import("@/views/AItrainingplan.vue"),
  },
  {
    path: "/customtrainingplan",
    name: "customtrainingplan",
    component: () => import("@/views/customtrainingplan.vue"),
  },
  {
    path: "/training",
    name: "training",
    component: () => import("@/views/training.vue"),
  },
  {
    path: "/customplan",
    name: "CustomPlan",
    component: () => import("@/views/CustomPlan.vue"),
  },
  {
    path: "/monitor",
    name: "monitor",
    component: () => import("@/views/monitor.vue"),
  },
  {
    path: "/aichoose",
    name: "AI choose",
    component: () => import("@/views/AI choose.vue"),
  },
  {
    path: "/assessment",
    name: "Assessment",
    component: () => import("@/views/Assessment.vue"),
  },
    {
    path: "/assessment2",
    name: "assessment2",
    component: () => import("@/views/assessment2.vue"),
  },
  {
    path: "/caiji",
    name: "Caiji",
    component: () => import("@/views/caiji.vue"),
  },
  {
    path: "/family",
    name: "Family",
    component: () => import("@/views/family.vue"),
  },
  {
    path: "/doctor",
    name: "Doctor",
    component: () => import("@/views/doctor.vue"),
  },
  {
    path: "/personal",
    name: "personal",
    component: () => import("@/views/personal.vue"),
  },
  {
    path: "/history",
    name: "history",
    component: () => import("@/views/history.vue"),
  },
  {
    path: "/wear",
    name: "wear",
    component: () => import("@/views/wear.vue"),
  },
  {
    path: "/planchoose",
    name: "planchoose",
    component: () => import("@/views/planchoose.vue"),
  },
  {
    path: "/attempt",
    name: "attempt",
    component: () => import("@/views/attempt.vue"),
  },
  {
    path: "/breakbeginning",
    name: "breakbeginning",
    component: () => import("@/views/breakbeginning.vue"),
  },
  {
    path: "/breakend",
    name: "breakend",
    component: () => import("@/views/breakend.vue"),
  },
  {
    path: "/generatingplan",
    name: "generatingplan",
    component: () => import("@/views/generatingplan.vue"),
  },
  {
    path: "/generatingreport",
    name: "generatingreport",
    component: () => import("@/views/generatingreport.vue"),
  },
  {
    path: "/report",
    name: "report",
    component: () => import("@/views/report.vue"),
  },
  {
    path: "/test_age",
    name: "test_age",
    component: () => import("@/views/test_age.vue"),
  },
  {
    path: "/test_caiji",
    name: "test_caiji",
    component: () => import("@/views/test_caiji.vue"),
  },
  {
    path: "/test_peidai",
    name: "test_peidai",
    component: () => import("@/views/test_peidai.vue"),
  },
  {
    path: "/test_try",
    name: "test_try",
    component: () => import("@/views/test_try.vue"),
  },
  {
    path: "/test_kangfu",
    name: "test_kangfu",
    component: () => import("@/views/test_kangfu.vue"),
  },
    {
    path: "/ht2pdf",
    name: "ht2pdf",
    component: () => import("@/views/ht2pdf.vue"),
  },
  {
    path: "/doctor_front",
    name: "doctor_front",
    component: () => import("@/views/doctor_front.vue"),
  },
  {
    path: "/add_patient",
    name: "add_patient",
    component: () => import("@/views/add_patient.vue"),
  },
  {
    path: "/description",
    name: "description",
    component: () => import("@/views/description.vue"),
  },
  {
    path: "/record_advice",
    name: "record_advice",
    component: () => import("@/views/record_advice.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
