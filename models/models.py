from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    balance = Column(Integer, default=0)
    current_tool_id = Column(UUID(as_uuid=True),  ForeignKey("tools.id"), nullable=True)
    current_location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)

    player_achievements = relationship("PlayerAchievement", back_populates="player")
    current_tool = relationship("Tool", back_populates="players")
    current_location = relationship("Location", back_populates="players")
    tools = relationship("PlayerTool", back_populates="player")
    locations = relationship("PlayerLocation", back_populates="player")

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(String)
    reward = Column(Integer)
    image_url = Column(String)
    player_achievements = relationship("PlayerAchievement", back_populates="achievement")


class PlayerAchievement(Base):
    __tablename__ = "player_achievements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id"))

    player = relationship("Player", back_populates="player_achievements")
    achievement = relationship("Achievement", back_populates="player_achievements")


class Location(Base):
    __tablename__ = "locations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(String)
    multiplier = Column(Integer)
    image_url = Column(String)

    players = relationship("Player", back_populates="current_location")
    player_locations = relationship("PlayerLocation", back_populates="location")



class PlayerLocation(Base):
    __tablename__ = "player_locations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"))

    player = relationship("Player", back_populates="locations")
    location = relationship("Location", back_populates="player_locations")

class PlayerTool(Base):
    __tablename__ = "player_tools"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id"))

    player = relationship("Player", back_populates="tools")
    tool = relationship("Tool", back_populates="player_tools")

# class Statistics(Base):
#     __tablename__ = "statistics"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
#     clicks = Column(Integer)
#     score = Column(Integer)

class Tool(Base):
    __tablename__ = "tools"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(String)
    cost = Column(Integer)
    efficiency = Column(Integer)
    image_url = Column(String)

    players = relationship("Player", back_populates="current_tool")
    player_tools = relationship("PlayerTool", back_populates="tool")

from pydantic import BaseModel
from uuid import UUID

class PlayerInfo(BaseModel):
    id: UUID
    username: str
    balance: int = 0
    current_tool_id: UUID
    current_location_id: UUID

# class Achievements(BaseModel):
#     id: UUID
#     name: str
#     description: str
#     reward: int
#
# class PlayerAchievements(BaseModel):
#     id: UUID
#     player_id: UUID
#     achievement_id: UUID

    class Config:
        from_attributes = True
