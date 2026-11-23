import { Route, Routes } from "react-router";
import { RequireAuth } from "./auth/RequireAuth";
import { AuthLayout } from "./components/AuthLayout";
import { Layout } from "./components/Layout";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { PostDetailPage } from "./pages/PostDetailPage";
import { PostFormPage } from "./pages/PostFormPage";
import { PostListPage } from "./pages/PostListPage";
import { SignupPage } from "./pages/SignupPage";

// 주소(URL) ↔ 화면 연결표
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<PostListPage />} />
        <Route
          path="posts/new"
          element={
            <RequireAuth>
              <PostFormPage />
            </RequireAuth>
          }
        />
        <Route path="posts/:id" element={<PostDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
      <Route element={<AuthLayout />}>
        <Route path="login" element={<LoginPage />} />
        <Route path="signup" element={<SignupPage />} />
      </Route>
    </Routes>
  );
}
