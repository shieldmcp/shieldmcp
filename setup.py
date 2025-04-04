from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# ASCII Art for the package
ASCII_ART = r"""

 .S_SsS_S.     sSSs   .S_sSSs      sSSs    sSSs    sSSs   .S       S.    .S_sSSs      sSSs  
.SS~S*S~SS.   d%%SP  .SS~YS%%b    d%%SP   d%%SP   d%%SP  .SS       SS.  .SS~YS%%b    d%%SP  
S%S `Y' S%S  d%S'    S%S   `S%b  d%S'    d%S'    d%S'    S%S       S%S  S%S   `S%b  d%S'    
S%S     S%S  S%S     S%S    S%S  S%|     S%S     S%S     S%S       S%S  S%S    S%S  S%S     
S%S     S%S  S&S     S%S    d*S  S&S     S&S     S&S     S&S       S&S  S%S    d*S  S&S     
S&S     S&S  S&S     S&S   .S*S  Y&Ss    S&S_Ss  S&S     S&S       S&S  S&S   .S*S  S&S_Ss  
S&S     S&S  S&S     S&S_sdSSS   `S&&S   S&S~SP  S&S     S&S       S&S  S&S_sdSSS   S&S~SP  
S&S     S&S  S&S     S&S~YSSY      `S*S  S&S     S&S     S&S       S&S  S&S~YSY%b   S&S     
S*S     S*S  S*b     S*S            l*S  S*b     S*b     S*b       d*S  S*S   `S%b  S*b     
S*S     S*S  S*S.    S*S           .S*P  S*S.    S*S.    S*S.     .S*S  S*S    S%S  S*S.    
S*S     S*S   SSSbs  S*S         sSS*S    SSSbs   SSSbs   SSSbs_sdSSS   S*S    S&S   SSSbs  
SSS     S*S    YSSP  S*S         YSS'      YSSP    YSSP    YSSP~YSSY    S*S    SSS    YSSP  
        SP           SP                                                 SP                  
        Y            Y                                                  Y                   
                                                                                            

"""

setup(
    name="mcp-secure",
    version="0.1.0",
    author="x3at",
    author_email="xiomaraengine@gmail.com",
    description=ASCII_ART + "\nA security middleware for Model Context Protocol (MCP) servers that enhances security and monitoring capabilities without modifying the official SDK. This package provides tools for securing and monitoring MCP tool calls, following the best practices outlined in the MCP documentation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/n3-n2-n1/mcp-secure",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "structlog>=21.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.5b2",
            "isort>=5.9.3",
            "mypy>=0.910",
            "flake8>=3.9.2",
        ],
    },
) 