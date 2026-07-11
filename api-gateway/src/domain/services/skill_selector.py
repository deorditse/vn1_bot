from common.enums import SkillEnum


class SkillSelector:
    def select(
        self,
        requested_skill: SkillEnum | None,
        question: str,
        available_skills: list[SkillEnum],
    ) -> SkillEnum:
        if requested_skill:
            return requested_skill
        if SkillEnum.gitlab in available_skills and SkillEnum.gitlab.value in question.lower():
            return SkillEnum.gitlab
        return available_skills[0]
