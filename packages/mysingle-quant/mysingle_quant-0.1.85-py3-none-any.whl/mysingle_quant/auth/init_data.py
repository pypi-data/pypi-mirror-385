from ..core.config import settings
from ..core.logging_config import get_logger
from .models import User
from .security.password import PasswordHelper

password_helper = PasswordHelper()

logger = get_logger(__name__)


async def create_first_super_admin() -> None:
    """첫 번째 Super Admin 사용자 생성"""
    try:
        logger.info("Checking for existing Super Admin user...")

        # 설정 값 확인
        if (
            settings.SUPERUSER_EMAIL == "your_email@example.com"
            or settings.SUPERUSER_PASSWORD == "change-this-admin-password"
        ):
            logger.warning(
                "Super Admin creation skipped: Default email/password values detected. "
                "Please set SUPERUSER_EMAIL and SUPERUSER_PASSWORD environment variables."
            )
            return

        logger.info(f"Creating Super Admin with email: {settings.SUPERUSER_EMAIL}")

        # 기존 Super Admin 사용자 확인 (이메일 기준)
        existing_super_admin = await User.find_one({"email": settings.SUPERUSER_EMAIL})
        if existing_super_admin:
            logger.info(
                f"✅ Super Admin user already exists: {existing_super_admin.email}"
            )
            return

        # Super Admin User 생성
        logger.info("Creating new Super Admin user...")
        user = User(
            email=settings.SUPERUSER_EMAIL,
            hashed_password=password_helper.hash(settings.SUPERUSER_PASSWORD),
            full_name=settings.SUPERUSER_FULLNAME,
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )

        await user.save()
        logger.info(f"✅ Super Admin user created: {user.full_name} ({user.email})")

        logger.info(
            f"✅ First Super Admin created successfully: {settings.SUPERUSER_EMAIL}"
        )

    except Exception as e:
        logger.error(
            f"❌ Failed to create first Super Admin: {type(e).__name__}: {str(e)}"
        )
        logger.error(f"Settings - Email: {settings.SUPERUSER_EMAIL}")
        logger.error(f"Settings - Fullname: {settings.SUPERUSER_FULLNAME}")
        # Super Admin 생성 실패가 애플리케이션 시작을 막지 않도록 함
        # raise e  # 주석 처리하여 애플리케이션이 계속 시작되도록 함


async def create_test_users() -> None:
    """
    테스트용 유저 생성 (development/local 환경에서만)

    생성되는 테스트 유저:
    1. test_user: 일반 유저 (verified, not superuser)
       - email: "test_user"
       - password: "1234"
       - full_name: "Test User"

    2. test_admin: 관리자 유저 (verified, superuser)
       - email: "test_admin"
       - password: "1234"
       - full_name: "Test Admin"

    ⚠️ WARNING: production 환경에서는 절대 호출되지 않습니다!
    """
    # production 환경에서는 실행 안 함
    if settings.ENVIRONMENT.lower() not in ["development", "local", "dev"]:
        logger.info(
            "⏭️ Test user creation skipped: Not in development/local environment"
        )
        return

    try:
        logger.info("🧪 Creating test users for development/local environment...")

        # 1. 일반 테스트 유저 생성
        existing_test_user = await User.find_one({"email": settings.TEST_USER_EMAIL})
        if existing_test_user:
            logger.info(f"✅ Test user already exists: {settings.TEST_USER_EMAIL}")
        else:
            test_user = User(
                email=settings.TEST_USER_EMAIL,
                hashed_password=password_helper.hash(settings.TEST_USER_PASSWORD),
                full_name=settings.TEST_USER_FULLNAME,
                is_active=True,
                is_superuser=False,
                is_verified=True,
            )
            await test_user.save()
            logger.info(
                f"✅ Test user created: {settings.TEST_USER_FULLNAME} ({settings.TEST_USER_EMAIL})"
            )

        # 2. 관리자 테스트 유저 생성
        existing_test_admin = await User.find_one({"email": settings.TEST_ADMIN_EMAIL})
        if existing_test_admin:
            logger.info(f"✅ Test admin already exists: {settings.TEST_ADMIN_EMAIL}")
        else:
            test_admin = User(
                email=settings.TEST_ADMIN_EMAIL,
                hashed_password=password_helper.hash(settings.TEST_ADMIN_PASSWORD),
                full_name=settings.TEST_ADMIN_FULLNAME,
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            await test_admin.save()
            logger.info(
                f"✅ Test admin created: {settings.TEST_ADMIN_FULLNAME} ({settings.TEST_ADMIN_EMAIL})"
            )

        logger.info("✅ Test users setup completed successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create test users: {type(e).__name__}: {str(e)}")
        # 테스트 유저 생성 실패가 애플리케이션 시작을 막지 않도록 함
