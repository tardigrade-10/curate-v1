from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import datetime
import json

Base = declarative_base()

class Service(Base):
    __tablename__ = 'services'

    id = Column(UUID(as_uuid=True), primary_key=True)
    service_name = Column(String, nullable=False)
    description = Column(String)
    config_options = Column(JSON, default={})
    input_spec = Column(JSON, default={})
    output_spec = Column(JSON, default={})
    status = Column(String, default='active')  # or 'inactive', 'error', etc.
    service_type = Column(String, nullable=False)  # Can be 'ML', 'Processing', 'Engine', etc.
    usage_count = Column(Integer, default=0)
    usage_limit = Column(Integer, nullable=True)  # if you want to have a limit, else it can be nullable
    cost_per_use = Column(Float, nullable=False)
    last_used = Column(DateTime, default=datetime.datetime.utcnow)

    def execute(self, input):
        """
        Execute the service with given input.
        This is a placeholder and would need the specific logic for service execution.
        """
        # Placeholder logic
        return NotImplementedError("Method not found")

    def validate_input(self, input):
        """
        Validate input against the input_spec.
        """
        for key, value in self.input_spec.items():
            if key not in input or not isinstance(input[key], value):
                return False
        return True

    def get_default_config(self):
        """
        Return the default configuration.
        """
        return self.config_options

    def update_config(self, new_config):
        """
        Update the current configuration with new_config.
        """
        self.config_options.update(new_config)
        # Make sure to add logic to commit the changes to the database

    def get_service_status(self):
        """
        Return the current status of the service.
        """
        return self.status

    def toggle_status(self):
        """
        Toggle the service status between 'active' and 'inactive'.
        """
        self.status = 'inactive' if self.status == 'active' else 'active'
        # Again, remember to commit the changes to the database

    def on_error(self, error):
        """
        Handle any error that arises when using the service.
        """
        self.status = 'error'
        # Here, you might want to log the error or notify someone.
        # Make sure to commit the changes to the database

    def increment_usage(self):
        """
        Increase the usage_count by 1.
        """
        self.usage_count += 1
        self.last_used = datetime.datetime.utcnow()
        # Commit the changes to the database

    def check_usage_limit(self):
        """
        Check if the usage count has exceeded the usage limit.
        """
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return True
        return False

    def calculate_cost(self):
        """
        Calculate the cost of using the service once.
        """
        return self.cost_per_use

    def alert_usage_limit(self):
        """
        Send an alert when the usage limit is near or exceeded.
        """
        # You would integrate with a notification or alerting system here
        pass

    def send_usage_summary(self):
        """
        Send a summary of the service usage.
        """
        # Integrate with a reporting system or email service to send the usage summary
        pass

    def use_service(self, workspace):
        """
        Use the service and deduct the cost from the workspace balance.
        This will also check if there's enough balance to run the service.
        """
        cost = self.calculate_cost()
        if workspace.balance >= cost:
            workspace.balance -= cost
            self.increment_usage()
            # Execute the service here and handle errors
            # Commit the changes to the database
            return {"success": True, "message": "Service executed successfully"}
        else:
            return {"success": False, "message": "Insufficient balance"}

# You would need a corresponding Workspace model with a balance field to use the use_service method.

# Note: Remember to add logic to commit the changes to the database wherever required.

