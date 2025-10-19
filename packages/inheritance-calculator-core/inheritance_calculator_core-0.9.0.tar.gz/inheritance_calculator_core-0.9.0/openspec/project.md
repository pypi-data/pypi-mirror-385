# inheritance-calculator-core

日本の民法に基づく相続計算のコアライブラリ

## Project Overview

`inheritance-calculator-core`は、日本の民法に基づいた相続人の資格確定と相続割合の計算を行うPythonライブラリです。

### Core Capabilities
- 相続人資格の判定（配偶者、子、直系尊属、兄弟姉妹）
- 相続割合の計算（法定相続分）
- 代襲相続の処理
- 再転相続の処理
- Neo4jデータベース統合
- AI対話インターフェース（オプション）

### Technology Stack
- **Language**: Python 3.12+
- **Framework**: Pydantic for data validation
- **Database**: Neo4j (graph database)
- **Testing**: pytest with 100% coverage
- **AI**: Ollama integration (optional)

### Architecture
```
src/inheritance_calculator_core/
├── models/          # Pydantic data models
├── services/        # Business logic layer
├── database/        # Neo4j integration (repositories, queries)
├── agents/          # AI conversation interface
└── utils/           # Utilities (config, logging, exceptions)
```

### Key Design Principles
- **Domain-Driven Design**: Clear separation of domain logic
- **Repository Pattern**: Database abstraction
- **Service Layer**: Business logic orchestration
- **Type Safety**: Pydantic models with strict validation

## Current State

### Strengths
- ✅ 100% test coverage
- ✅ Comprehensive Japanese civil law implementation
- ✅ Neo4j graph database integration
- ✅ Clean model layer with Pydantic

### Known Issues
- ⚠️ Large monolithic calculator method (605 lines)
- ⚠️ Type safety issues with ID conversions
- ⚠️ Incomplete dependency injection
- ⚠️ Code duplication in retransfer logic
- ⚠️ Repository pattern encapsulation violations

## Development Guidelines

### Code Quality Standards
- Type hints required for all functions
- 100% test coverage maintained
- Follow Japanese civil law accurately
- Document民法条文references in code

### Testing Standards
- Unit tests for all business logic
- Integration tests for database operations
- Edge case coverage for legal scenarios
- Validation of法定相続分calculations
