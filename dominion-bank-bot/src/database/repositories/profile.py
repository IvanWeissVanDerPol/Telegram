"""
The Phantom Bot - Profile and Settings Repositories
"""
from typing import Optional

from src.database.models import Profile, UserSettings
from src.database.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    """Repository for Profile operations."""

    model = Profile

    async def get_or_create(self, user_id: int) -> Profile:
        """Get or create profile for user."""
        profile = await self.session.get(Profile, user_id)
        if profile:
            return profile

        profile = Profile(user_id=user_id)
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update(
        self,
        user_id: int,
        **kwargs,
    ) -> Optional[Profile]:
        """Update profile fields."""
        profile = await self.session.get(Profile, user_id)
        if not profile:
            return None

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        # Calculate completeness
        fields = ['display_name', 'pronouns', 'age', 'location', 'main_role',
                  'experience_level', 'bio', 'looking_for']
        filled = sum(1 for f in fields if getattr(profile, f, None))
        profile.profile_completeness = int((filled / len(fields)) * 100)

        await self.session.flush()
        return profile


class UserSettingsRepository(BaseRepository[UserSettings]):
    """Repository for UserSettings operations."""

    model = UserSettings

    async def get_or_create(self, user_id: int) -> UserSettings:
        """Get or create settings for user."""
        settings = await self.session.get(UserSettings, user_id)
        if settings:
            return settings

        settings = UserSettings(user_id=user_id)
        self.session.add(settings)
        await self.session.flush()
        return settings

    async def update(
        self,
        user_id: int,
        **kwargs,
    ) -> Optional[UserSettings]:
        """Update settings fields."""
        settings = await self.session.get(UserSettings, user_id)
        if not settings:
            return None

        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        await self.session.flush()
        return settings
