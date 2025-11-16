from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, DateTime,
    Boolean, JSON, ForeignKey, TIMESTAMP, func, Float
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))

    business_type = Column(String(50), default="ИП")
    industry = Column(String(100))
    business_size = Column(String(50))
    monthly_revenue = Column(Integer)

    language = Column(String(10), default="ru")
    notifications_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    business_data = relationship(
        "BusinessData",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    quick_actions = relationship(
        "QuickAction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="user", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"

    def __str__(self):
        return f"Пользователь {self.username or self.id} ({self.first_name or ''} {self.last_name or ''})"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))

    category = Column(String(50))
    user_message = Column(Text)
    bot_response = Column(Text)
    message_length = Column(Integer)
    response_time_ms = Column(Integer)
    last_message_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation id={self.id} user_id={self.user_id} category='{self.category}'>"

    def __str__(self):
        created = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"Диалог #{self.id}: [{self.category}] — {created}"


class BusinessData(Base):
    __tablename__ = "business_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))

    data_type = Column(String(50))
    period = Column(String(20))
    period_date = Column(DateTime)
    data_json = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="business_data")

    def __repr__(self):
        return f"<BusinessData id={self.id} user_id={self.user_id} type='{self.data_type}'>"

    def __str__(self):
        return f"Бизнес-данные ({self.data_type}, период: {self.period})"


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    category = Column(String(50))
    content = Column(Text)
    suitable_for = Column(JSON)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Template id={self.id} name='{self.name}'>"

    def __str__(self):
        return f"Шаблон: {self.name} [{self.category}]"


class QuickAction(Base):
    __tablename__ = "quick_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))

    action_type = Column(String(50))
    action_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quick_actions")

    def __repr__(self):
        return f"<QuickAction id={self.id} user_id={self.user_id} type='{self.action_type}'>"

    def __str__(self):
        return f"Быстрое действие: {self.action_type}"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))

    filename = Column(String(255))
    file_type = Column(String(20))  # pdf, docx, jpg...
    content_text = Column(Text)  # распознанный/вытащенный текст
    size_bytes = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    insights = relationship("Insight", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document id={self.id} file='{self.filename}' user_id={self.user_id}>"

    def __str__(self):
        size = f"{self.size_bytes / 1024:.1f} KB" if self.size_bytes else "?"
        return f"Документ: {self.filename} ({self.file_type}, {size})"


class Insight(Base):
    __tablename__ = "document_insights"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    summary = Column(Text)
    risks = Column(Text)
    recommendations = Column(Text)
    raw_data = Column(Text)  # сырой JSON от ИИ
    created_at = Column(DateTime, default=func.now())

    document = relationship("Document", back_populates="insights")

    def __repr__(self):
        return f"<DocumentInsight id={self.id} document_id={self.document_id}>"

    def __str__(self):
        return f"Инсайты по документу #{self.document_id}"


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    agent = Column(String(50))  # legal, marketing, risk, editor, finance
    input_text = Column(Text)
    output_text = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

    def __repr__(self):
        return f"<AgentLog id={self.id} user_id={self.user_id} agent='{self.agent}'>"

    def __str__(self):
        return f"Лог агента [{self.agent}] для пользователя {self.user_id}"


class MarketingIdeas(Base):
    __tablename__ = "marketing_ideas"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)

    niche = Column(Text)
    goal = Column(Text)
    platform = Column(Text)
    custom_request = Column(Text)

    idea_title = Column(Text)
    idea_description = Column(Text)
    idea_examples = Column(Text)

    created_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<MarketingIdeas id={self.id} user_id={self.user_id}>"

    def __str__(self):
        return f"Маркетинговая идея для пользователя {self.user_id}: {self.idea_title}"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="Разное")
    purchase_price = Column(Float, default=0.0)
    selling_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    user = relationship("User")
    def __repr__(self):
        return f"<Product id={self.id} name='{self.name}'>"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    customer_info = Column(String(255), nullable=True)
    payment_method = Column(String(50), default="cash")

    # Связи
    product = relationship("Product", back_populates="sales")
    user = relationship("User")
    def __repr__(self):
        return f"<Sale id={self.id} product_id={self.product_id} amount={self.total_amount}>"


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)  # incoming, outgoing, adjustment
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255))
    date = Column(DateTime, default=datetime.utcnow)

    # Связи
    product = relationship("Product", back_populates="stock_movements")
    user = relationship("User")
    def __repr__(self):
        return f"<StockMovement id={self.id} product_id={self.product_id} type={self.type}>"