## 1. 회의 정보

---

- **회의 목적:** 진행 상황 보고 및 해야 할 일 정리
- **참석자:** 고은희, 김나은, 성유리, 윤예린, 김하람, 백수진
- **회의 시간:** 2026.11.23 14:00

## 2. 회의 내용

---

### 현재 진행 상황 보고

1. CI/CD
    - 진행 상태: CI/CD 파이프라인 구축 및 자동 배포 검증 완료
        - GCP VM 인스턴스 생성 및 Jenkins 서버 구축
        - Jenkins와 GitHub 연동 (Webhook, GitHub App)
        - Docker Hub 및 GKE Credential 등록
        - Jenkins 컨테이너 내 gcloud, kubectl 설치 및 GKE 연결
        - Jenkinsfile 기반 CI/CD 파이프라인 구축
            - Checkout → Build → Test → Push → Deploy
        - PR 생성 시 자동 빌드 및 테스트, GitHub Checks 연동
        - main 브랜치 머지 시 Docker Hub 이미지 Push 및 GKE dev 환경 자동 배포
        - 전체 파이프라인 5단계 정상 동작 검증 완료
        - CI/CD 파이프라인 및 개인 Jenkins 실습 가이드 문서화
2. Infrastructure / Cloud
    - 진행 상태: 클라우드 인프라 및 배포 환경 구축 완료
        - Docker Hub 기반 백엔드·프론트엔드 이미지 저장소 구성
        - Kubernetes 매니페스트 수정 및 최신 이미지 반영 설정
        - 단일 GKE 클러스터 구축
        - 공용 네임스페이스(dev, prod) 및 팀원별 개인 네임스페이스 구성
        - 네임스페이스별 ConfigMap, Secret, Service, PostgreSQL DB 사전 배포
        - 팀원별 GCP 서비스 계정 생성 및 최소 권한 부여
        - 미사용 시간대 워커 노드 수 조정을 통한 GCP 비용 최적화
        - GKE 인프라 및 개인 네임스페이스 사용 가이드 문서화
3. Backend
    - 진행 상태: 주요 서비스 기능 구현 완료
        - 초기 세팅 - Django REST Framework, Docker 개발 환경 구축 완료
        - 이메일 기반 User 모델 구현 완료
        - 회원가입, 로그인, 게시물, 알림 처리 기능 구현 완료
        - 규칙 기반 유사도 점수 계산 및 매칭 후보 API 완료
        - 매칭 알고리즘 구현 현황
            - 종류(40점), 색상(25점), 장소(20점), 날짜(15점) 기반 유사도 계산
            - 50점 이상 매칭 후보 표시, 70점 이상 인앱 알림 발송
            - 게시물 등록·수정 시 자동 매칭 재계산
            - 중복 매칭 및 중복 알림 방지 로직 구현
4. Frontend
    - 초기 세팅 - Vite + React, ESLint, React Router
    - 회원가입, 로그인, 게시물 목록, 게시물 상세, 게시물 등록 기능 구현 완료
    - 게시물 목록, 게시물 상세, 게시물 등록 backend와 연동 완료
    - 회원가입/로그인 화면 구현 완료 - 인증 API 연동은 백엔드 구현 대기 중

## 3. 결정사항

---

- CI/CD 파이프라인 구축은 팀원 전원이 레포지토리 fork를 통해 진행
- 개인 구축하며 발견한 개선점을 중앙 레포지토리에 올리기
- 클러스터는 하나만 (크레딧 절약) - 네임스페이스만 분할

## 4. 해야 할 일

---

- 자동 배포 단계에 DB 마이그레이션 추가
- 개인 네임스페이스 배포 테스트 및 관리
- CI/CD - 팀원별 Fork 후 개인 CI/CD 실습
- FE & BE - 학교 이메일 인증 및 JWT 로그인 API 구현
- BE - GCS 기반 이미지 업로드 구현
- FE - 인증 API 및 알림 기능 연동
- FE - UI/UX 디자인 확정
- 전체 서비스 통합 테스트 및 배포 검증
