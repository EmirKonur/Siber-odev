# Smart City Automation System with Digital Banking Integration

A comprehensive Python-based web application simulating a smart city infrastructure with integrated digital banking, designed for Vercel deployment.

## Features

- **Smart City Control**: Remote control of city infrastructure (lights, traffic, security)
- **Digital Banking**: Fiat and cryptocurrency payment processing
- **Security**: Multi-factor authentication, role-based access, encryption
- **Real-time Notifications**: Observer pattern for alerts and updates
- **AI Analytics**: Predictive insights for city management

## Design Patterns Used

- **Singleton**: CityController for centralized management
- **Command**: Infrastructure operations (lights, traffic, payments)
- **Observer**: Security and transaction notifications
- **Adapter**: Multi-cryptocurrency integration
- **Template Method**: Daily automated routines

## Project Structure

```
├── app/                    # Main application
│   ├── models/            # Data models
│   ├── controllers/       # Business logic
│   ├── services/          # Service layer
│   ├── commands/          # Command pattern
│   ├── routines/          # Template method
│   ├── security/          # Auth & encryption
│   └── templates/         # HTML templates
├── static/                # CSS/JS assets
├── uml/                   # PlantUML diagrams
├── api/                   # Vercel serverless
└── tests/                 # Unit tests
```

## Installation

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
python -m flask --app app.main run --debug
```

## Vercel Deployment

The application is configured for Vercel serverless deployment:

```bash
vercel dev      # Local development
vercel          # Deploy to production
```

## UML Diagrams

PlantUML diagrams are available in the `/uml` directory:
- `class_diagram.puml` - System class structure
- `sequence_diagram.puml` - Key operation flows
- `usecase_diagram.puml` - Actor interactions
- `component_diagram.puml` - System architecture

Render at: https://www.plantuml.com/plantuml/uml/

## License

MIT License
