
# Import all the models, so that Base has them before creating tables
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.patient import Patient  # noqa
from app.models.image import Image  # noqa
from app.models.analysis import Analysis  # noqa
from app.models.report import Report  # noqa
from app.models.notification import Notification  # noqa
from app.models.activity_log import ActivityLog  # noqa
from app.models.model_version import ModelVersion  # noqa
