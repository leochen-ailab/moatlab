import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings, loaded from environment variables."""

    anthropic_api_key: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", "")
    )
    anthropic_base_url: str | None = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_BASE_URL")
    )

    # Model selection
    default_model: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    )
    deep_analysis_model: str = "claude-opus-4-6"

    # Analysis defaults
    margin_of_safety_target: float = 0.30  # 30% 安全边际
    max_portfolio_positions: int = 15  # 巴菲特式集中持仓
    dcf_discount_rate: float = 0.10  # 10% 折现率
    dcf_terminal_growth_rate: float = 0.03  # 3% 永续增长率
    dcf_projection_years: int = 10

    # Portfolio database
    db_path: str = field(
        default_factory=lambda: os.environ.get("MOATLAB_DB_PATH", "~/.moatlab/portfolio.db")
    )

    # SEC EDGAR identity (required by SEC fair access policy)
    sec_edgar_identity: str = field(
        default_factory=lambda: os.environ.get("SEC_EDGAR_IDENTITY", "MoatLab moatlab@example.com")
    )

    # Lark Bot
    lark_app_id: str = field(default_factory=lambda: os.environ.get("LARK_APP_ID", ""))
    lark_app_secret: str = field(default_factory=lambda: os.environ.get("LARK_APP_SECRET", ""))
    lark_verification_token: str = field(
        default_factory=lambda: os.environ.get("LARK_VERIFICATION_TOKEN", "")
    )
    lark_encrypt_key: str = field(default_factory=lambda: os.environ.get("LARK_ENCRYPT_KEY", ""))


settings = Settings()
