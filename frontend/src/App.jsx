import { Route, Routes, useParams } from "react-router";
import { RequireAuth } from "./auth/RequireAuth";
import { AuthLayout } from "./components/AuthLayout";
import { Layout } from "./components/Layout";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { PostDetailPage } from "./pages/PostDetailPage";
import { PostFormPage } from "./pages/PostFormPage";
import { PostListPage } from "./pages/PostListPage";
import { SignupPage } from "./pages/SignupPage";

// /posts/1 → /posts/2 로 이동하면 React 는 같은 화면을 재사용해서 이전 게시물 상태가 남음
// key 를 게시물 id 로 주면 id 가 바뀔 때 화면을 새로 만들어 상태(데이터·에러·삭제 중)가 초기화됨
function PostDetailRoute() {
  const { id } = useParams();
  return <PostDetailPage key={id} />;
}

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
        <Route path="posts/:id" element={<PostDetailRoute />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
      <Route element={<AuthLayout />}>
        <Route path="login" element={<LoginPage />} />
        <Route path="signup" element={<SignupPage />} />
      </Route>
    </Routes>
  );
}
