import json
import os
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, ValidationError, PrivateAttr, field_validator, ValidationError
from sqlmodel import Field, Session, SQLModel, create_engine, select, JSON, DateTime, Column, ARRAY
from typing import Optional, List, Dict, Any, ClassVar
from datetime import datetime
import shutil
from os import PathLike
from sqlalchemy import Column, Integer
from sqlalchemy.orm import scoped_session, sessionmaker
import uuid
import re
from PIL import Image
import imagehash
import asyncio
from http import cookiejar
from importlib import import_module
from typing import TYPE_CHECKING, Annotated
from more_itertools import first_true
from random import randint
from sqlalchemy.sql.type_api import Variant
from collections import defaultdict
import customtkinter
from tkinter import ttk
from tkinter import filedialog
import re