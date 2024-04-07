from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
import streamlit as st

T = TypeVar("T")


class Session(BaseModel, Generic[T]):
    name: str
    value: Optional[T] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.name not in st.session_state:
            st.session_state[self.name] = self.value
        else:
            self.state = st.session_state[self.name]

    class Config:
        arbitrary_types_allowed = True

    @property
    def state(self) -> T:
        return self.value

    @state.setter
    def state(self, value: T) -> None:
        st.session_state[self.name] = value
        self.value = value
