"""
Session management for ConvAI Innovations platform.
"""

from typing import Dict, List, Optional
from .models import Session, LearningProgress


class SessionManager:
    """Manages learning sessions and progression"""
    
    def __init__(self):
        self.sessions = self._create_sessions()
        self.progress = LearningProgress(total_sessions=len(self.sessions))
        
    def _create_sessions(self) -> Dict[str, Session]:
        """Create all learning sessions with visualization types"""
        sessions = {}
        
        # Session 1: Python Fundamentals
        sessions["python_fundamentals"] = Session(
            id="python_fundamentals",
            title="🐍 Python Fundamentals",
            description="""
# Python Fundamentals for Machine Learning

Learn essential Python concepts needed for ML/AI development:
- Variables and data types
- Functions and classes
- Lists and dictionaries
- Control flow (loops, conditionals)
- File handling and imports

These fundamentals are crucial for understanding ML code!
""",
            reference_code="""# Python Fundamentals for ML/AI
# Variables and data types essential for ML
learning_rate = 0.001  # float for hyperparameters
batch_size = 32        # int for training
model_name = "GPT"     # string for identifiers
is_training = True     # boolean for flags

# Lists for storing data (like training examples)
training_data = [1, 2, 3, 4, 5]
layer_sizes = [784, 256, 128, 10]

# Dictionaries for configuration
config = {
    "learning_rate": 0.001,
    "epochs": 100,
    "optimizer": "adam"
}

# Functions (building blocks of ML code)
def calculate_accuracy(predictions, targets):
    correct = sum(p == t for p, t in zip(predictions, targets))
    return correct / len(targets)

# Classes for organizing ML components
class ModelConfig:
    def __init__(self, lr=0.001, epochs=100):
        self.learning_rate = lr
        self.epochs = epochs
        self.optimizer = "adam"
    
    def __str__(self):
        return f"Config(lr={self.learning_rate}, epochs={self.epochs})"

# Test the concepts
predictions = [1, 0, 1, 1, 0]
targets = [1, 0, 1, 0, 0]
accuracy = calculate_accuracy(predictions, targets)
model_config = ModelConfig()

print(f"Training data: {training_data}")
print(f"Model accuracy: {accuracy:.2f}")
print(f"Configuration: {model_config}")
print(f"Layer sizes: {layer_sizes}")""",
            learning_objectives=[
                "Understand variable types used in ML",
                "Write functions for ML computations", 
                "Use classes to organize code",
                "Work with lists and dictionaries",
                "Apply Python basics to ML scenarios"
            ],
            hints=[
                "Variables store values - think of them as labeled boxes",
                "Functions help organize code - like recipes for computations",
                "Classes group related functions and data together",
                "Lists store sequences - perfect for datasets",
                "Dictionaries store key-value pairs - great for configs"
            ],
            visualization_type="python_basics"
        )
        
        # Session 2: PyTorch and NumPy Operations
        sessions["pytorch_numpy"] = Session(
            id="pytorch_numpy",
            title="🔢 PyTorch & NumPy Operations",
            description="""
# PyTorch and NumPy Fundamentals

Master tensor operations and numerical computing:
- Creating and manipulating tensors
- Mathematical operations
- Reshaping and indexing
- Broadcasting and reduction operations
- GPU acceleration basics

Foundation for all neural network computations!
""",
            reference_code="""# PyTorch and NumPy Operations for Deep Learning
import torch
import numpy as np

print("🔢 Tensor Creation and Basic Operations")

# Creating tensors (the building blocks of neural networks)
tensor_1d = torch.tensor([1, 2, 3, 4, 5])
tensor_2d = torch.tensor([[1, 2], [3, 4], [5, 6]])
random_tensor = torch.randn(3, 4)  # Random normal distribution
zeros_tensor = torch.zeros(2, 3)
ones_tensor = torch.ones(4, 4)

print(f"1D tensor: {tensor_1d}")
print(f"2D tensor shape: {tensor_2d.shape}")
print(f"Random tensor:\\n{random_tensor}")

# Mathematical operations (essential for neural networks)
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

# Element-wise operations
addition = a + b
multiplication = a * b
power = torch.pow(a, 2)

print(f"\\nElement-wise addition: {addition}")
print(f"Element-wise multiplication: {multiplication}")
print(f"Square: {power}")

# Matrix operations (core of neural networks)
matrix_a = torch.randn(3, 4)
matrix_b = torch.randn(4, 2)
matrix_product = torch.matmul(matrix_a, matrix_b)  # Matrix multiplication

print(f"\\nMatrix multiplication result shape: {matrix_product.shape}")

# Reshaping (crucial for neural network layers)
original = torch.randn(2, 3, 4)
reshaped = original.view(2, 12)  # Flatten last two dimensions
flattened = original.flatten()

print(f"Original shape: {original.shape}")
print(f"Reshaped: {reshaped.shape}")
print(f"Flattened: {flattened.shape}")

# Reduction operations (used in loss functions)
data = torch.randn(3, 4)
mean_val = torch.mean(data)
sum_val = torch.sum(data)
max_val = torch.max(data)

print(f"\\nMean: {mean_val:.4f}")
print(f"Sum: {sum_val:.4f}")
print(f"Max: {max_val:.4f}")

# Gradients (automatic differentiation for learning)
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2 + 3 * x + 1
y.backward()  # Compute dy/dx

print(f"\\nInput: {x.item()}")
print(f"Output: {y.item()}")
print(f"Gradient dy/dx: {x.grad.item()}")""",
            learning_objectives=[
                "Create and manipulate PyTorch tensors",
                "Perform mathematical operations on tensors",
                "Understand matrix multiplication for neural networks",
                "Master reshaping and indexing operations",
                "Learn automatic differentiation basics"
            ],
            hints=[
                "Tensors are like NumPy arrays but with GPU support and gradients",
                "Matrix multiplication is the core operation in neural networks",
                "View() and reshape() change tensor dimensions without copying data",
                "requires_grad=True enables automatic gradient computation",
                "Always check tensor shapes - mismatched shapes cause errors"
            ],
            visualization_type="tensor_operations"
        )
        
        # Session 3: Neural Network Fundamentals
        sessions["neural_networks"] = Session(
            id="neural_networks",
            title="🧠 Neural Network Fundamentals",
            description="""
# Neural Network Building Blocks

Understand the core components of neural networks:
- Perceptrons and multi-layer networks
- Linear layers and activations
- Forward propagation
- nn.Module and PyTorch structure
- Simple network architectures

Building towards transformer understanding!
""",
            reference_code="""# Neural Network Fundamentals with PyTorch
import torch
import torch.nn as nn
import torch.nn.functional as F

print("🧠 Neural Network Building Blocks")

# Single neuron (perceptron) - the basic unit
class Perceptron(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.linear = nn.Linear(input_size, 1)  # W*x + b
    
    def forward(self, x):
        return torch.sigmoid(self.linear(x))  # Sigmoid activation

# Multi-layer neural network
class SimpleNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.layer2 = nn.Linear(hidden_size, hidden_size)
        self.layer3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        # Forward propagation through layers
        x = F.relu(self.layer1(x))      # Hidden layer 1 + ReLU
        x = self.dropout(x)             # Dropout for regularization
        x = F.relu(self.layer2(x))      # Hidden layer 2 + ReLU
        x = self.layer3(x)              # Output layer (no activation)
        return x

# Create sample data
batch_size = 4
input_size = 10
hidden_size = 20
output_size = 5

# Sample input (like features from an embedding)
sample_input = torch.randn(batch_size, input_size)

print(f"Input shape: {sample_input.shape}")

# Test perceptron
perceptron = Perceptron(input_size)
perceptron_output = perceptron(sample_input)
print(f"Perceptron output shape: {perceptron_output.shape}")

# Test multi-layer network
model = SimpleNet(input_size, hidden_size, output_size)
output = model(sample_input)
print(f"Multi-layer network output shape: {output.shape}")

# Count parameters (important for understanding model size)
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"\\nModel Architecture:")
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")

# Demonstrate parameter access
print(f"\\nFirst layer weights shape: {model.layer1.weight.shape}")
print(f"First layer bias shape: {model.layer1.bias.shape}")

# Show how gradients work
loss = torch.mean(output ** 2)  # Dummy loss
loss.backward()

print(f"\\nAfter backward pass:")
print(f"First layer weight gradients shape: {model.layer1.weight.grad.shape}")
print("✅ Neural network fundamentals complete!")""",
            learning_objectives=[
                "Understand perceptrons and multi-layer networks",
                "Build networks using nn.Module",
                "Implement forward propagation",
                "Use activation functions effectively",
                "Count and understand model parameters"
            ],
            hints=[
                "nn.Linear performs matrix multiplication: y = Wx + b",
                "Activation functions add non-linearity between layers",
                "nn.Module is the base class for all neural network components",
                "Forward() defines how data flows through the network",
                "Dropout prevents overfitting by randomly zeroing neurons"
            ],
            visualization_type="neural_network"
        )
        
        # Session 4: Backpropagation
        sessions["backpropagation"] = Session(
            id="backpropagation",
            title="⬅️ Backpropagation",
            description="""
# Backpropagation - How Neural Networks Learn

Understanding the learning mechanism:
- Chain rule and gradients
- Forward and backward passes
- Gradient computation
- Parameter updates
- Manual vs automatic differentiation

The foundation of all neural network training!
""",
            reference_code="""# Backpropagation - How Neural Networks Learn
import torch
import torch.nn as nn

print("⬅️ Understanding Backpropagation")

# Simple example to demonstrate backpropagation
class TinyNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.w1 = nn.Parameter(torch.tensor([[0.5, -0.2], [0.3, 0.1]]))
        self.b1 = nn.Parameter(torch.tensor([0.1, -0.1]))
        self.w2 = nn.Parameter(torch.tensor([[0.4], [0.6]]))
        self.b2 = nn.Parameter(torch.tensor([0.0]))
    
    def forward(self, x):
        # Forward pass step by step
        z1 = torch.matmul(x, self.w1) + self.b1  # Linear transformation
        a1 = torch.relu(z1)                       # Activation
        z2 = torch.matmul(a1, self.w2) + self.b2 # Output layer
        return z2

# Create model and data
model = TinyNetwork()
x = torch.tensor([[1.0, 0.5]])  # Input
target = torch.tensor([[1.0]])   # Target output

print("Initial parameters:")
print(f"W1: {model.w1.data}")
print(f"W2: {model.w2.data}")

# Forward pass
output = model(x)
print(f"\\nForward pass:")
print(f"Input: {x}")
print(f"Output: {output}")
print(f"Target: {target}")

# Compute loss
loss = 0.5 * (output - target) ** 2  # MSE loss
print(f"Loss: {loss.item():.4f}")

# Backward pass (automatic differentiation)
loss.backward()

print(f"\\nGradients after backward pass:")
print(f"dL/dW1: {model.w1.grad}")
print(f"dL/dW2: {model.w2.grad}")

# Manual parameter update (what optimizers do)
learning_rate = 0.1
with torch.no_grad():
    model.w1 -= learning_rate * model.w1.grad
    model.w2 -= learning_rate * model.w2.grad
    model.b1 -= learning_rate * model.b1.grad
    model.b2 -= learning_rate * model.b2.grad

print(f"\\nParameters after update:")
print(f"Updated W1: {model.w1.data}")
print(f"Updated W2: {model.w2.data}")

# Demonstrate the complete training step
def training_step(model, x, target, lr=0.1):
    # Zero gradients
    model.zero_grad()
    
    # Forward pass
    output = model(x)
    loss = 0.5 * (output - target) ** 2
    
    # Backward pass
    loss.backward()
    
    # Update parameters
    with torch.no_grad():
        for param in model.parameters():
            param -= lr * param.grad
    
    return loss.item()

# Train for a few steps
print(f"\\nTraining demonstration:")
for step in range(5):
    loss_val = training_step(model, x, target)
    output = model(x)
    print(f"Step {step+1}: Loss = {loss_val:.4f}, Output = {output.item():.4f}")

print("\\n✅ Backpropagation complete! This is how all neural networks learn.")""",
            learning_objectives=[
                "Understand gradient computation through chain rule",
                "See how forward and backward passes work together",
                "Learn parameter update mechanics",
                "Compare manual vs automatic differentiation",
                "Implement a complete training step"
            ],
            hints=[
                "Forward pass: compute output from input",
                "Backward pass: compute gradients from loss to parameters",
                "Chain rule: multiply gradients through connected operations",
                "Zero gradients before each backward pass",
                "Parameter update: param = param - lr * gradient"
            ],
            visualization_type="backpropagation"
        )

        # Session 5: Python Data Structures for AI
        sessions["python_data_structures"] = Session(
            id="python_data_structures",
            title="📚 Python Data Structures",
            description="""
# Advanced Python Data Structures for AI

Master data structures essential for ML/AI:
- Lists, tuples, and sets
- Dictionary operations
- List comprehensions
- Nested structures
- Data manipulation

Critical for handling datasets and model configurations!
""",
            reference_code="""# Data Structures for AI/ML
import numpy as np

# Lists - mutable sequences (datasets)
training_samples = [28, 64, 128, 256, 512]
validation_split = [0.8, 0.2]

# Tuples - immutable (image dimensions, model architecture)
input_shape = (224, 224, 3)
hidden_layers = (512, 256, 128)

# Sets - unique elements (vocabulary, unique labels)
unique_labels = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
vocabulary = set(["hello", "world", "AI", "learning"])

# Dictionaries - configurations and mappings
model_config = {
    "layers": [128, 64, 32],
    "activation": "relu",
    "dropout": 0.5,
    "optimizer": "adam"
}

# List comprehensions - efficient data processing
squared_data = [x**2 for x in training_samples]
normalized = [x / max(training_samples) for x in training_samples]

# Nested structures - complex data
dataset = {
    "train": {"images": [], "labels": []},
    "val": {"images": [], "labels": []},
    "test": {"images": [], "labels": []}
}

# Dictionary operations
model_config["learning_rate"] = 0.001
model_config.update({"batch_size": 32, "epochs": 100})

# Filtering data
large_batches = [b for b in training_samples if b > 100]

# Print results
print(f"Training samples: {training_samples}")
print(f"Input shape: {input_shape}")
print(f"Unique labels: {sorted(unique_labels)}")
print(f"Model config: {model_config}")
print(f"Normalized: {normalized}")
print(f"Large batches: {large_batches}")""",
            learning_objectives=[
                "Use lists for sequential data storage",
                "Apply tuples for immutable configurations",
                "Leverage sets for unique elements",
                "Master dictionary operations",
                "Write list comprehensions efficiently"
            ],
            hints=[
                "Lists are mutable - great for growing datasets",
                "Tuples are immutable - perfect for fixed shapes",
                "Sets automatically remove duplicates",
                "Dictionaries map keys to values - ideal for configs",
                "List comprehensions are faster than loops"
            ],
            visualization_type="python_basics"
        )

        # Session 6: NumPy Fundamentals
        sessions["numpy_fundamentals"] = Session(
            id="numpy_fundamentals",
            title="🔢 NumPy Fundamentals",
            description="""
# NumPy - Foundation of ML

NumPy is the backbone of ML in Python:
- Array creation and manipulation
- Mathematical operations
- Broadcasting
- Indexing and slicing
- Statistical functions

99% of ML libraries use NumPy!
""",
            reference_code="""# NumPy Fundamentals for ML
import numpy as np

# Creating arrays (tensors in ML)
data = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2, 3], [4, 5, 6]])
zeros = np.zeros((3, 3))
ones = np.ones((2, 4))
random_data = np.random.randn(5, 5)

# Array properties
print(f"Shape: {matrix.shape}")
print(f"Dimensions: {matrix.ndim}")
print(f"Data type: {matrix.dtype}")

# Mathematical operations
a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])

addition = a + b
multiplication = a * b
dot_product = np.dot(a, b)
mean = np.mean(a)
std = np.std(a)

# Reshaping (critical for ML)
flattened = matrix.flatten()
reshaped = data.reshape(5, 1)

# Indexing and slicing
first_row = matrix[0, :]
first_column = matrix[:, 0]
subset = random_data[:3, :3]

# Broadcasting (auto size matching)
normalized = (random_data - np.mean(random_data)) / np.std(random_data)

# Boolean indexing (filtering)
positive_only = random_data[random_data > 0]

# Statistical operations
matrix_sum = np.sum(matrix)
column_means = np.mean(matrix, axis=0)
row_maxs = np.max(matrix, axis=1)

# Print results
print(f"Addition: {addition}")
print(f"Dot product: {dot_product}")
print(f"Mean: {mean:.2f}, Std: {std:.2f}")
print(f"Column means: {column_means}")
print(f"Normalized shape: {normalized.shape}")""",
            learning_objectives=[
                "Create and manipulate NumPy arrays",
                "Perform vectorized operations",
                "Understand broadcasting rules",
                "Apply statistical functions",
                "Master array indexing and slicing"
            ],
            hints=[
                "Arrays are faster than lists for math",
                "Use reshape() to change dimensions",
                "Broadcasting avoids explicit loops",
                "axis=0 is rows, axis=1 is columns",
                "Boolean indexing filters data efficiently"
            ],
            visualization_type="neural_network"
        )

        # Session 7: Data Loading and Preprocessing
        sessions["data_preprocessing"] = Session(
            id="data_preprocessing",
            title="🔄 Data Preprocessing",
            description="""
# Data Preprocessing for ML

Learn to prepare data for machine learning:
- Loading data from files
- Handling missing values
- Normalization and scaling
- Data splitting
- Feature extraction

Clean data = Better models!
""",
            reference_code="""# Data Preprocessing for ML
import numpy as np

# Simulating raw data (normally loaded from CSV/files)
raw_data = np.array([
    [1.0, 2.5, 100],
    [2.0, 3.1, 150],
    [1.5, np.nan, 120],
    [3.0, 4.2, 200],
    [2.5, 3.8, 180]
])

labels = np.array([0, 1, 0, 1, 1])

# Step 1: Handle missing values
mean_val = np.nanmean(raw_data[:, 1])
data_cleaned = raw_data.copy()
data_cleaned[np.isnan(data_cleaned)] = mean_val

# Step 2: Normalization (scale to 0-1)
def normalize(data):
    min_vals = np.min(data, axis=0)
    max_vals = np.max(data, axis=0)
    return (data - min_vals) / (max_vals - min_vals + 1e-8)

normalized_data = normalize(data_cleaned)

# Step 3: Standardization (mean=0, std=1)
def standardize(data):
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    return (data - mean) / (std + 1e-8)

standardized_data = standardize(data_cleaned)

# Step 4: Train-test split (80-20)
split_idx = int(0.8 * len(normalized_data))
X_train = normalized_data[:split_idx]
X_test = normalized_data[split_idx:]
y_train = labels[:split_idx]
y_test = labels[split_idx:]

# Step 5: One-hot encoding for labels
def one_hot_encode(labels, num_classes=2):
    encoded = np.zeros((len(labels), num_classes))
    encoded[np.arange(len(labels)), labels] = 1
    return encoded

y_train_encoded = one_hot_encode(y_train)

# Print results
print(f"Original data shape: {raw_data.shape}")
print(f"Cleaned data (no NaN): {np.isnan(data_cleaned).sum()} missing")
print(f"Normalized data range: [{normalized_data.min():.2f}, {normalized_data.max():.2f}]")
print(f"Standardized mean: {standardized_data.mean():.4f}")
print(f"Train set size: {len(X_train)}, Test set size: {len(X_test)}")
print(f"One-hot encoded labels:\n{y_train_encoded}")""",
            learning_objectives=[
                "Handle missing data properly",
                "Normalize and standardize features",
                "Split data into train/test sets",
                "One-hot encode categorical labels",
                "Prepare data pipelines for ML"
            ],
            hints=[
                "Always handle NaN values before training",
                "Normalization brings values to 0-1 range",
                "Standardization makes mean=0, std=1",
                "80-20 split is common for train/test",
                "One-hot encoding for categorical targets"
            ],
            visualization_type="neural_network"
        )

        # Session 8: Linear Regression (First ML Model)
        sessions["linear_regression"] = Session(
            id="linear_regression",
            title="📈 Linear Regression",
            description="""
# Your First ML Model: Linear Regression

Build a machine learning model from scratch:
- Understanding linear models
- Gradient descent optimization
- Loss function (MSE)
- Training loop
- Making predictions

The foundation of all ML algorithms!
""",
            reference_code="""# Linear Regression from Scratch
import numpy as np

# Generate synthetic data: y = 3x + 2 + noise
np.random.seed(42)
X = np.random.randn(100, 1) * 2
y = 3 * X + 2 + np.random.randn(100, 1) * 0.5

# Model parameters
weights = np.random.randn(1, 1)
bias = np.zeros((1, 1))
learning_rate = 0.01
epochs = 100

# Training function
def train_step(X, y, weights, bias, lr):
    # Forward pass: y_pred = Xw + b
    y_pred = np.dot(X, weights) + bias

    # Compute loss (Mean Squared Error)
    loss = np.mean((y_pred - y) ** 2)

    # Backward pass (gradients)
    dw = (2 / len(X)) * np.dot(X.T, (y_pred - y))
    db = (2 / len(X)) * np.sum(y_pred - y)

    # Update parameters
    weights = weights - lr * dw
    bias = bias - lr * db

    return weights, bias, loss

# Training loop
print("Training Linear Regression...")
for epoch in range(epochs):
    weights, bias, loss = train_step(X, y, weights, bias, learning_rate)

    if epoch % 20 == 0:
        print(f"Epoch {epoch}, Loss: {loss:.4f}")

# Final model
print(f"\nLearned parameters:")
print(f"Weight: {weights[0, 0]:.2f} (true: 3.0)")
print(f"Bias: {bias[0, 0]:.2f} (true: 2.0)")

# Make predictions
X_test = np.array([[0], [1], [2]])
y_pred = np.dot(X_test, weights) + bias
print(f"\nPredictions for X={X_test.flatten()}:")
print(f"y_pred = {y_pred.flatten()}")

# Calculate R² score
y_pred_train = np.dot(X, weights) + bias
ss_res = np.sum((y - y_pred_train) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r2_score = 1 - (ss_res / ss_tot)
print(f"\nR² Score: {r2_score:.4f}")""",
            learning_objectives=[
                "Understand linear model basics",
                "Implement gradient descent",
                "Calculate MSE loss",
                "Train a model with iterations",
                "Evaluate model performance"
            ],
            hints=[
                "Linear model: y = wx + b",
                "Gradient descent updates parameters",
                "MSE measures prediction error",
                "Lower loss = better model",
                "R² score shows goodness of fit"
            ],
            visualization_type="neural_network"
        )

        # Session 9: Classification with Logistic Regression
        sessions["logistic_regression"] = Session(
            id="logistic_regression",
            title="🎯 Logistic Regression",
            description="""
# Classification: Logistic Regression

Build a classification model:
- Sigmoid activation function
- Binary classification
- Cross-entropy loss
- Decision boundaries
- Accuracy metrics

From regression to classification!
""",
            reference_code="""# Logistic Regression for Classification
import numpy as np

# Generate binary classification data
np.random.seed(42)
X_class0 = np.random.randn(50, 2) + np.array([2, 2])
X_class1 = np.random.randn(50, 2) + np.array([0, 0])
X = np.vstack([X_class0, X_class1])
y = np.vstack([np.zeros((50, 1)), np.ones((50, 1))])

# Sigmoid activation
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Model parameters
weights = np.random.randn(2, 1) * 0.01
bias = np.zeros((1, 1))
learning_rate = 0.1
epochs = 1000

# Training function
def train_logistic(X, y, weights, bias, lr):
    # Forward pass
    z = np.dot(X, weights) + bias
    y_pred = sigmoid(z)

    # Binary cross-entropy loss
    epsilon = 1e-7
    loss = -np.mean(y * np.log(y_pred + epsilon) + (1 - y) * np.log(1 - y_pred + epsilon))

    # Gradients
    dz = y_pred - y
    dw = (1 / len(X)) * np.dot(X.T, dz)
    db = (1 / len(X)) * np.sum(dz)

    # Update
    weights = weights - lr * dw
    bias = bias - lr * db

    return weights, bias, loss

# Training loop
print("Training Logistic Regression...")
for epoch in range(epochs):
    weights, bias, loss = train_logistic(X, y, weights, bias, learning_rate)

    if epoch % 200 == 0:
        print(f"Epoch {epoch}, Loss: {loss:.4f}")

# Make predictions
z = np.dot(X, weights) + bias
y_pred_prob = sigmoid(z)
y_pred_class = (y_pred_prob > 0.5).astype(int)

# Calculate accuracy
accuracy = np.mean(y_pred_class == y)
print(f"\nTraining Accuracy: {accuracy * 100:.2f}%")

# Test on new points
X_test = np.array([[2, 2], [0, 0], [1, 1]])
z_test = np.dot(X_test, weights) + bias
probs = sigmoid(z_test)
predictions = (probs > 0.5).astype(int)

print(f"\nTest predictions:")
for i, (point, prob, pred) in enumerate(zip(X_test, probs, predictions)):
    print(f"Point {point}: Probability={prob[0]:.2f}, Class={pred[0]}")""",
            learning_objectives=[
                "Understand sigmoid activation",
                "Implement binary classification",
                "Use cross-entropy loss",
                "Calculate classification accuracy",
                "Make probabilistic predictions"
            ],
            hints=[
                "Sigmoid squashes output to 0-1",
                "Threshold at 0.5 for binary decision",
                "Cross-entropy for classification loss",
                "Accuracy = correct predictions / total",
                "Probabilities indicate confidence"
            ],
            visualization_type="neural_network"
        )

        # Session 10: Model Evaluation Metrics
        sessions["model_evaluation"] = Session(
            id="model_evaluation",
            title="📊 Model Evaluation",
            description="""
# Evaluating ML Models

Learn to measure model performance:
- Accuracy, Precision, Recall
- F1 Score
- Confusion Matrix
- ROC and AUC
- Cross-validation

Don't just train - evaluate properly!
""",
            reference_code="""# Model Evaluation Metrics
import numpy as np

# Simulated predictions and true labels
np.random.seed(42)
y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
y_pred = np.array([1, 0, 1, 0, 0, 1, 0, 1, 1, 1])

# Confusion Matrix
def confusion_matrix(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return tp, tn, fp, fn

tp, tn, fp, fn = confusion_matrix(y_true, y_pred)

# Metrics
accuracy = (tp + tn) / (tp + tn + fp + fn)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

# K-Fold Cross Validation
def kfold_split(data, k=5):
    fold_size = len(data) // k
    indices = np.arange(len(data))
    np.random.shuffle(indices)

    folds = []
    for i in range(k):
        start = i * fold_size
        end = start + fold_size if i < k-1 else len(data)
        test_idx = indices[start:end]
        train_idx = np.concatenate([indices[:start], indices[end:]])
        folds.append((train_idx, test_idx))

    return folds

# Example: 5-fold CV
data = np.arange(20)
folds = kfold_split(data, k=5)

# Mean Absolute Error
def mae(y_true, y_pred):
    return np.mean(np.abs(y_true - y_pred))

# Mean Squared Error
def mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

# R² Score
def r2_score(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

# Print results
print("Confusion Matrix:")
print(f"TP: {tp}, TN: {tn}")
print(f"FP: {fp}, FN: {fn}\n")

print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1 Score: {f1_score:.3f}\n")

print(f"Created {len(folds)} folds for cross-validation")
print(f"Each test fold has ~{len(folds[0][1])} samples")""",
            learning_objectives=[
                "Calculate confusion matrix",
                "Compute accuracy, precision, recall",
                "Understand F1 score",
                "Implement k-fold cross-validation",
                "Use appropriate metrics for tasks"
            ],
            hints=[
                "Confusion matrix shows all outcomes",
                "Precision: how many predicted positives are correct",
                "Recall: how many actual positives found",
                "F1: harmonic mean of precision and recall",
                "Cross-validation prevents overfitting"
            ],
            visualization_type="neural_network"
        )

        # Session 11: Regularization
        sessions["regularization"] = Session(
            id="regularization",
            title="🎯 Regularization",
            description="""
# Regularization - Preventing Overfitting

Techniques to improve model generalization:
- L1 and L2 regularization
- Dropout
- Weight decay
- Early stopping
- Data augmentation

Critical for production models!
""",
            reference_code="""# Regularization Techniques
import torch
import torch.nn as nn
import torch.nn.functional as F

print("Regularization - Preventing Overfitting")

# L2 Regularization (Weight Decay)
class RegularizedNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.5)  # Dropout regularization

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)  # Randomly zero 50% of neurons
        x = self.fc2(x)
        return x

# Create model
model = RegularizedNet(784, 128, 10)

# L2 regularization via weight_decay in optimizer
import torch.optim as optim
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=0.01)

# L1 Regularization (manual)
def l1_regularization(model, lambda_l1=0.01):
    l1_loss = 0
    for param in model.parameters():
        l1_loss += torch.sum(torch.abs(param))
    return lambda_l1 * l1_loss

# L2 Regularization (manual)
def l2_regularization(model, lambda_l2=0.01):
    l2_loss = 0
    for param in model.parameters():
        l2_loss += torch.sum(param ** 2)
    return lambda_l2 * l2_loss

# Example training with regularization
x = torch.randn(32, 784)
y = torch.randint(0, 10, (32,))

# Forward pass
output = model(x)
loss_ce = F.cross_entropy(output, y)

# Add regularization
loss_l1 = l1_regularization(model)
loss_l2 = l2_regularization(model)
total_loss = loss_ce + loss_l1 + loss_l2

print(f"Cross-entropy loss: {loss_ce.item():.4f}")
print(f"L1 penalty: {loss_l1.item():.4f}")
print(f"L2 penalty: {loss_l2.item():.4f}")
print(f"Total loss: {total_loss.item():.4f}")

# Dropout demonstration
model.training = True  # Dropout active
output_train = model(x)
model.training = False   # Dropout disabled
output_eval = model(x)

print(f"\\nTrain mode output: {output_train[0, :3]}")
print(f"Eval mode output: {output_eval[0, :3]}")
print("Regularization prevents overfitting!")""",
            learning_objectives=[
                "Understand L1 and L2 regularization",
                "Implement dropout correctly",
                "Use weight decay in optimizers",
                "Prevent overfitting in models",
                "Choose appropriate regularization"
            ],
            hints=[
                "L1 creates sparse weights",
                "L2 shrinks large weights",
                "Dropout prevents co-adaptation",
                "weight_decay = L2 regularization",
                "Use model.training to toggle train/inference mode"
            ],
            visualization_type="neural_network"
        )

        # Session 12: Loss Functions & Optimizers
        sessions["loss_optimizers"] = Session(
            id="loss_optimizers",
            title="📉 Loss & Optimizers",
            description="""
# Loss Functions and Optimizers

Learn the engines of neural network training:
- MSE, Cross-Entropy, and custom losses
- SGD, Adam, AdamW optimizers
- Learning rate schedules
- Gradient clipping
- Optimizer comparison

Choose the right tools for training!
""",
            reference_code="""# Loss Functions and Optimizers
import torch
import torch.nn as nn
import torch.optim as optim

print("Loss Functions and Optimizers")

# Common Loss Functions
x = torch.randn(10, 5)
target_regression = torch.randn(10, 5)
target_classification = torch.randint(0, 5, (10,))

# 1. Mean Squared Error (Regression)
mse_loss = nn.MSELoss()
loss_mse = mse_loss(x, target_regression)
print(f"MSE Loss: {loss_mse.item():.4f}")

# 2. Cross-Entropy (Classification)
ce_loss = nn.CrossEntropyLoss()
loss_ce = ce_loss(x, target_classification)
print(f"Cross-Entropy Loss: {loss_ce.item():.4f}")

# 3. Binary Cross-Entropy
bce_loss = nn.BCEWithLogitsLoss()
binary_target = torch.randint(0, 2, (10, 5)).float()
loss_bce = bce_loss(x, binary_target)
print(f"Binary CE Loss: {loss_bce.item():.4f}")

# Create a simple model for optimizer demo
class TinyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 5)

    def forward(self, x):
        return self.fc(x)

model = TinyModel()

# Different Optimizers
print("\\nOptimizer Comparison:")

# 1. SGD (Stochastic Gradient Descent)
optimizer_sgd = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
print("SGD: Classic, reliable, needs tuning")

# 2. Adam (Adaptive Moment Estimation)
optimizer_adam = optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.999))
print("Adam: Adaptive learning rates, popular choice")

# 3. AdamW (Adam with Weight Decay)
optimizer_adamw = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
print("AdamW: Adam + better L2 regularization")

# Learning Rate Scheduler
scheduler = optim.lr_scheduler.StepLR(optimizer_adam, step_size=10, gamma=0.1)

# Training step with gradient clipping
def train_step(model, x, y, optimizer):
    optimizer.zero_grad()
    output = model(x)
    loss = nn.CrossEntropyLoss()(output, y)
    loss.backward()

    # Gradient clipping (prevents exploding gradients)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

    optimizer.step()
    return loss.item()

# Example training
x_batch = torch.randn(4, 10)
y_batch = torch.randint(0, 5, (4,))
loss = train_step(model, x_batch, y_batch, optimizer_adam)
print(f"\\nTraining step loss: {loss:.4f}")

# Learning rate scheduling
for epoch in range(5):
    current_lr = optimizer_adam.param_groups[0]['lr']
    print(f"Epoch {epoch}: LR = {current_lr:.6f}")
    scheduler.step()

print("Loss functions measure error, optimizers minimize it!")""",
            learning_objectives=[
                "Choose appropriate loss functions",
                "Understand different optimizers",
                "Implement learning rate schedules",
                "Apply gradient clipping",
                "Optimize training hyperparameters"
            ],
            hints=[
                "MSE for regression, CE for classification",
                "Adam is a great default optimizer",
                "AdamW is better for transformers",
                "Clip gradients to prevent explosions",
                "Learning rate decay improves convergence"
            ],
            visualization_type="neural_network"
        )

        # Session 13: LLM Architecture
        sessions["llm_architecture"] = Session(
            id="llm_architecture",
            title="🏗️ LLM Architecture",
            description="""
# Large Language Model Architecture

Understanding modern LLM components:
- Transformer architecture overview
- Self-attention mechanism
- Multi-head attention
- Feedforward networks
- Layer normalization

Foundation of GPT, BERT, and all modern LLMs!
""",
            reference_code="""# LLM Architecture Components
import torch
import torch.nn as nn
import math

print("LLM Architecture - Transformer Building Blocks")

class TransformerConfig:
    def __init__(self):
        self.vocab_size = 50000
        self.d_model = 512      # Model dimension
        self.n_heads = 8        # Number of attention heads
        self.d_ff = 2048        # Feedforward dimension
        self.n_layers = 6       # Number of transformer layers
        self.max_seq_len = 512  # Maximum sequence length
        self.dropout = 0.1

config = TransformerConfig()

# 1. Self-Attention Mechanism (Simplified)
class SelfAttention(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.d_model = d_model
        self.query = nn.Linear(d_model, d_model)
        self.key = nn.Linear(d_model, d_model)
        self.value = nn.Linear(d_model, d_model)

    def forward(self, x):
        # x shape: (batch, seq_len, d_model)
        Q = self.query(x)  # Queries
        K = self.key(x)    # Keys
        V = self.value(x)  # Values

        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_model)
        attn_weights = torch.softmax(scores, dim=-1)

        # Apply attention to values
        output = torch.matmul(attn_weights, V)
        return output, attn_weights

# 2. Multi-Head Attention
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.output = nn.Linear(d_model, d_model)

    def forward(self, x):
        batch_size, seq_len, d_model = x.shape

        # Generate Q, K, V
        qkv = self.qkv(x)  # (batch, seq_len, 3*d_model)
        qkv = qkv.reshape(batch_size, seq_len, 3, self.n_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # (3, batch, heads, seq_len, head_dim)
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Scaled dot-product attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(attn, v)

        # Concatenate heads
        out = out.transpose(1, 2).reshape(batch_size, seq_len, d_model)
        return self.output(out)

# 3. Feedforward Network
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # FFN(x) = max(0, xW1 + b1)W2 + b2
        return self.linear2(self.dropout(torch.relu(self.linear1(x))))

# Test the components
batch_size = 2
seq_len = 10
x = torch.randn(batch_size, seq_len, config.d_model)

print(f"Input shape: {x.shape}")

# Test self-attention
self_attn = SelfAttention(config.d_model)
attn_out, attn_weights = self_attn(x)
print(f"Self-Attention output: {attn_out.shape}")
print(f"Attention weights: {attn_weights.shape}")

# Test multi-head attention
mha = MultiHeadAttention(config.d_model, config.n_heads)
mha_out = mha(x)
print(f"Multi-Head Attention output: {mha_out.shape}")

# Test feedforward
ff = FeedForward(config.d_model, config.d_ff)
ff_out = ff(x)
print(f"FeedForward output: {ff_out.shape}")

# Count parameters
def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"\\nParameter counts:")
print(f"Multi-Head Attention: {count_parameters(mha):,}")
print(f"FeedForward: {count_parameters(ff):,}")
print("These are the core components of GPT, BERT, and all transformers!")""",
            learning_objectives=[
                "Understand transformer architecture",
                "Implement self-attention mechanism",
                "Build multi-head attention",
                "Create feedforward networks",
                "Grasp how LLMs process sequences"
            ],
            hints=[
                "Attention is query-key-value mechanism",
                "Multi-head = parallel attention",
                "FFN adds non-linearity",
                "Layer norm stabilizes training",
                "This architecture scales to billions of parameters"
            ],
            visualization_type="neural_network"
        )

        # Session 14: Tokenization & BPE
        sessions["tokenization_bpe"] = Session(
            id="tokenization_bpe",
            title="🔤 Tokenization & BPE",
            description="""
# Tokenization and Byte-Pair Encoding

How LLMs understand text:
- Text to tokens conversion
- Byte-Pair Encoding (BPE)
- Vocabulary building
- Special tokens
- Encoding and decoding

The first step in all NLP!
""",
            reference_code="""# Tokenization and Byte-Pair Encoding
import re
from collections import Counter

print("Tokenization & BPE - How LLMs Read Text")

# Simple word tokenization
text = "Hello world! How are you doing today? I'm learning about transformers."
words = re.findall(r"\\w+|[^\\w\\s]", text.lower())
print(f"Word tokens: {words[:10]}")

# Character-level tokenization
char_tokens = list("hello world")
print(f"Character tokens: {char_tokens}")

# Byte-Pair Encoding (BPE) - Simplified Implementation
class SimpleBPE:
    def __init__(self, vocab_size=100):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.merges = {}

    def get_stats(self, words):
        pairs = Counter()
        for word in words:
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i+1])] += 1
        return pairs

    def merge_vocab(self, pair, words):
        new_words = []
        bigram = ' '.join(pair)
        replacement = ''.join(pair)
        for word in words:
            new_word = word.replace(bigram, replacement)
            new_words.append(new_word)
        return new_words

    def build_vocab(self, corpus):
        # Start with character-level vocab
        words = [' '.join(word) + ' </w>' for word in corpus.split()]

        print(f"Initial: {words[:3]}")

        # Iteratively merge most frequent pairs
        for i in range(10):  # Simplified: only 10 merges
            pairs = self.get_stats(words)
            if not pairs:
                break

            best_pair = max(pairs, key=pairs.get)
            words = self.merge_vocab(best_pair, words)
            self.merges[best_pair] = i

            if i < 3:  # Show first 3 merges
                print(f"Merge {i+1}: {best_pair} -> {''.join(best_pair)}")

        print(f"Final: {words[:3]}")
        return words

# Build BPE vocab
corpus = "low lower lowest wide wider widest"
bpe = SimpleBPE()
vocab = bpe.build_vocab(corpus)

# Vocabulary with special tokens (like GPT)
special_tokens = {
    '<pad>': 0,   # Padding token
    '<sos>': 1,   # Start of sequence
    '<eos>': 2,   # End of sequence
    '<unk>': 3,   # Unknown token
    '<mask>': 4   # Mask token (for BERT)
}

print(f"\\nSpecial tokens: {special_tokens}")

# Token encoding example
def encode(text, vocab):
    # Simplified encoding
    tokens = text.lower().split()
    ids = [vocab.get(token, special_tokens['<unk>']) for token in tokens]
    return ids

def decode(ids, vocab):
    # Simplified decoding
    inv_vocab = {v: k for k, v in vocab.items()}
    tokens = [inv_vocab.get(id, '<unk>') for id in ids]
    return ' '.join(tokens)

# Example vocabulary (simplified)
simple_vocab = {
    'hello': 5, 'world': 6, 'transformer': 7,
    'learning': 8, 'ai': 9, 'model': 10
}
simple_vocab.update(special_tokens)

# Encode text
text = "hello world learning"
encoded = encode(text, simple_vocab)
print(f"\\nText: '{text}'")
print(f"Encoded: {encoded}")

# Decode back
decoded = decode(encoded, simple_vocab)
print(f"Decoded: '{decoded}'")

# Subword tokenization benefits
print(f"\\nBPE Benefits:")
print("- Handles unknown words via subwords")
print("- Smaller vocabulary size")
print("- Better for morphologically rich languages")
print("- Used in GPT, BERT, RoBERTa, etc.")
print("Tokenization is the foundation of all LLM processing!")""",
            learning_objectives=[
                "Understand tokenization process",
                "Learn Byte-Pair Encoding algorithm",
                "Build vocabulary from text",
                "Use special tokens correctly",
                "Encode and decode text"
            ],
            hints=[
                "Tokenization converts text to numbers",
                "BPE creates subword vocabulary",
                "Special tokens control sequences",
                "Vocabulary size affects model size",
                "Most LLMs use BPE or variants"
            ],
            visualization_type="neural_network"
        )

        # Session 15: RoPE & Attention
        sessions["rope_attention"] = Session(
            id="rope_attention",
            title="🔄 RoPE & Attention",
            description="""
# Rotary Position Embeddings & Attention

Advanced attention mechanisms:
- Positional encodings
- Rotary Position Embeddings (RoPE)
- Causal masking
- Attention patterns
- KV caching

Used in LLaMA, GPT-NeoX, and modern LLMs!
""",
            reference_code="""# RoPE and Advanced Attention
import torch
import torch.nn as nn
import math

print("RoPE & Attention - Advanced Position Encoding")

# Traditional Positional Encoding (Sinusoidal)
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        # x shape: (batch, seq_len, d_model)
        return x + self.pe[:x.size(1)]

# Rotary Position Embeddings (RoPE)
class RotaryPositionalEmbeddings(nn.Module):
    def __init__(self, dim, max_seq_len=2048):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self.max_seq_len = max_seq_len

    def forward(self, x, seq_len):
        # Generate rotation matrices
        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum('i,j->ij', t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        return emb.cos(), emb.sin()

# Apply RoPE to attention
def apply_rotary_pos_emb(q, k, cos, sin):
    def rotate_half(x):
        x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
        return torch.cat((-x2, x1), dim=-1)

    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed

# Causal Attention with RoPE
class CausalAttentionWithRoPE(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.rope = RotaryPositionalEmbeddings(self.head_dim)

    def forward(self, x):
        batch_size, seq_len, d_model = x.shape

        # Generate Q, K, V
        qkv = self.qkv(x).reshape(batch_size, seq_len, 3, self.n_heads, self.head_dim)
        q, k, v = qkv.permute(2, 0, 3, 1, 4)

        # Apply RoPE
        cos, sin = self.rope(x, seq_len)
        cos = cos[None, None, :, :]
        sin = sin[None, None, :, :]
        q, k = apply_rotary_pos_emb(q, k, cos, sin)

        # Attention scores
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # Causal mask (prevent attending to future tokens)
        causal_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
        scores = scores.masked_fill(causal_mask, float('-inf'))

        # Attention weights and output
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(attn, v)

        # Reshape and project
        out = out.transpose(1, 2).reshape(batch_size, seq_len, d_model)
        return self.out_proj(out)

# Test the components
d_model = 64
n_heads = 4
seq_len = 8
batch_size = 2

x = torch.randn(batch_size, seq_len, d_model)

print(f"Input shape: {x.shape}")

# Test traditional positional encoding
pos_enc = PositionalEncoding(d_model)
x_pos = pos_enc(x)
print(f"With positional encoding: {x_pos.shape}")

# Test RoPE attention
rope_attn = CausalAttentionWithRoPE(d_model, n_heads)
output = rope_attn(x)
print(f"RoPE Attention output: {output.shape}")

# Demonstrate causal masking
causal_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
print(f"\\nCausal mask shape: {causal_mask.shape}")
print(f"Causal mask:\\n{causal_mask.int()}")
print("RoPE improves positional encoding in modern LLMs!")""",
            learning_objectives=[
                "Understand positional encodings",
                "Implement Rotary Position Embeddings",
                "Apply causal masking for autoregressive models",
                "Build advanced attention mechanisms",
                "Grasp why RoPE is better than absolute positions"
            ],
            hints=[
                "Positional encoding adds position info",
                "RoPE rotates query and key embeddings",
                "Causal mask prevents future token access",
                "RoPE has better length extrapolation",
                "Used in LLaMA, GPT-NeoX, PaLM"
            ],
            visualization_type="neural_network"
        )

        # Session 16: RMS Normalization
        sessions["rms_normalization"] = Session(
            id="rms_normalization",
            title="📏 RMS Normalization",
            description="""
# Root Mean Square Normalization

Modern normalization techniques:
- Layer Normalization
- RMS Normalization
- Comparison with Batch Norm
- Pre-norm vs Post-norm
- Normalization in transformers

Critical for stable training!
""",
            reference_code="""# RMS Normalization and Layer Norm
import torch
import torch.nn as nn

print("RMS Normalization - Stabilizing Training")

# Layer Normalization (Standard)
class LayerNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(dim))
        self.beta = nn.Parameter(torch.zeros(dim))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        x_norm = (x - mean) / torch.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta

# RMS Normalization (Simpler, often better)
class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.scale = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        # RMS = sqrt(mean(x^2))
        rms = torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + self.eps)
        x_norm = x / rms
        return self.scale * x_norm

# Batch Normalization (for comparison)
class SimpleBatchNorm(nn.Module):
    def __init__(self, dim, eps=1e-5, momentum=0.1):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(dim))
        self.beta = nn.Parameter(torch.zeros(dim))
        self.eps = eps
        self.momentum = momentum
        self.register_buffer('running_mean', torch.zeros(dim))
        self.register_buffer('running_var', torch.ones(dim))

    def forward(self, x):
        # x shape: (batch, features)
        if self.training:
            mean = x.mean(dim=0)
            var = x.var(dim=0, unbiased=False)
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
        else:
            mean = self.running_mean
            var = self.running_var

        x_norm = (x - mean) / torch.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta

# Test data
batch_size = 4
seq_len = 8
d_model = 512
x = torch.randn(batch_size, seq_len, d_model)

print(f"Input shape: {x.shape}")
print(f"Input mean: {x.mean():.4f}, std: {x.std():.4f}")

# Test Layer Normalization
layer_norm = LayerNorm(d_model)
x_ln = layer_norm(x)
print(f"\\nLayer Norm output mean: {x_ln.mean():.4f}, std: {x_ln.std():.4f}")

# Test RMS Normalization
rms_norm = RMSNorm(d_model)
x_rms = rms_norm(x)
print(f"RMS Norm output mean: {x_rms.mean():.4f}, std: {x_rms.std():.4f}")

# Compare computational cost
import time

iterations = 1000
x_test = torch.randn(32, 128, 512)

# Layer Norm timing
start = time.time()
for _ in range(iterations):
    _ = layer_norm(x_test)
ln_time = time.time() - start

# RMS Norm timing
start = time.time()
for _ in range(iterations):
    _ = rms_norm(x_test)
rms_time = time.time() - start

print(f"\\nPerformance comparison ({iterations} iterations):")
print(f"Layer Norm: {ln_time:.4f}s")
print(f"RMS Norm: {rms_time:.4f}s")
print(f"Speedup: {ln_time/rms_time:.2f}x")

# Pre-norm vs Post-norm
class PreNormTransformerBlock(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.norm1 = RMSNorm(d_model)
        self.norm2 = RMSNorm(d_model)
        self.attn = nn.Linear(d_model, d_model)  # Simplified
        self.ffn = nn.Linear(d_model, d_model)

    def forward(self, x):
        # Pre-norm: normalize before each sublayer
        x = x + self.attn(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return x

print("\\nRMS Norm: Simpler and faster than Layer Norm!")
print("Used in LLaMA, GPT-NeoX, and other modern LLMs")""",
            learning_objectives=[
                "Understand Layer Normalization",
                "Implement RMS Normalization",
                "Compare different normalization techniques",
                "Learn pre-norm vs post-norm",
                "Apply normalization in transformers"
            ],
            hints=[
                "Normalization stabilizes training",
                "RMS Norm is faster than Layer Norm",
                "Pre-norm is now standard in LLMs",
                "No mean subtraction in RMS Norm",
                "Used in LLaMA and modern architectures"
            ],
            visualization_type="neural_network"
        )

        # Session 17: FFN & Activations
        sessions["ffn_activations"] = Session(
            id="ffn_activations",
            title="⚡ FFN & Activations",
            description="""
# Feedforward Networks and Activations

Understanding FFN and activation functions:
- Linear layers and transformations
- ReLU, GELU, SiLU activations
- Gated Linear Units (GLU)
- SwiGLU (used in LLaMA)
- FFN variants

The non-linearity in transformers!
""",
            reference_code="""# FFN and Activation Functions
import torch
import torch.nn as nn
import torch.nn.functional as F

print("FFN & Activations - Adding Non-Linearity")

# Different Activation Functions
x = torch.linspace(-3, 3, 100)

# 1. ReLU (Rectified Linear Unit)
relu_out = F.relu(x)

# 2. GELU (Gaussian Error Linear Unit)
gelu_out = F.gelu(x)

# 3. SiLU/Swish (Sigmoid Linear Unit)
silu_out = F.silu(x)

print("Activation Functions at x=1.0:")
print(f"ReLU: {F.relu(torch.tensor(1.0)):.4f}")
print(f"GELU: {F.gelu(torch.tensor(1.0)):.4f}")
print(f"SiLU: {F.silu(torch.tensor(1.0)):.4f}")

# Standard FFN (used in original Transformer)
class StandardFFN(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # FFN(x) = W2(Dropout(ReLU(W1(x))))
        return self.linear2(self.dropout(F.relu(self.linear1(x))))

# GELU FFN (used in GPT, BERT)
class GELUFFN(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.linear2(self.dropout(F.gelu(self.linear1(x))))

# Gated Linear Unit (GLU)
class GLU(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.linear_value = nn.Linear(d_model, d_ff)
        self.linear_gate = nn.Linear(d_model, d_ff)

    def forward(self, x):
        value = self.linear_value(x)
        gate = torch.sigmoid(self.linear_gate(x))
        return value * gate

# SwiGLU (used in LLaMA)
class SwiGLU(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.w1 = nn.Linear(d_model, d_ff, bias=False)
        self.w2 = nn.Linear(d_ff, d_model, bias=False)
        self.w3 = nn.Linear(d_model, d_ff, bias=False)

    def forward(self, x):
        # SwiGLU(x) = (Swish(xW1) ⊙ xW3)W2
        return self.w2(F.silu(self.w1(x)) * self.w3(x))

# Test the FFN variants
batch_size = 2
seq_len = 10
d_model = 512
d_ff = 2048

x = torch.randn(batch_size, seq_len, d_model)

print(f"\\nInput shape: {x.shape}")

# Test Standard FFN
standard_ffn = StandardFFN(d_model, d_ff)
out_standard = standard_ffn(x)
print(f"Standard FFN output: {out_standard.shape}")

# Test GELU FFN
gelu_ffn = GELUFFN(d_model, d_ff)
out_gelu = gelu_ffn(x)
print(f"GELU FFN output: {out_gelu.shape}")

# Test GLU
glu = GLU(d_model, d_ff)
out_glu = glu(x)
print(f"GLU output: {out_glu.shape}")

# Test SwiGLU
swiglu = SwiGLU(d_model, d_ff)
out_swiglu = swiglu(x)
print(f"SwiGLU output: {out_swiglu.shape}")

# Count parameters
def count_params(model):
    return sum(p.numel() for p in model.parameters())

print(f"\\nParameter counts:")
print(f"Standard FFN: {count_params(standard_ffn):,}")
print(f"GELU FFN: {count_params(gelu_ffn):,}")
print(f"SwiGLU: {count_params(swiglu):,}")

print("\\nActivation characteristics:")
print("- ReLU: Simple, fast, but can die")
print("- GELU: Smooth, used in GPT/BERT")
print("- SiLU/Swish: Smooth, self-gated")
print("- SwiGLU: Best for LLMs (LLaMA, PaLM)")
print("Choice of activation affects model quality!")""",
            learning_objectives=[
                "Understand feedforward networks",
                "Compare activation functions",
                "Implement Gated Linear Units",
                "Build SwiGLU (LLaMA activation)",
                "Choose appropriate activations"
            ],
            hints=[
                "FFN adds non-linearity between attention",
                "GELU is smoother than ReLU",
                "SwiGLU gates information flow",
                "LLaMA uses SwiGLU activation",
                "Activation choice affects quality"
            ],
            visualization_type="neural_network"
        )

        # Session 18: Training LLMs
        sessions["training_llms"] = Session(
            id="training_llms",
            title="🚀 Training LLMs",
            description="""
# Training Large Language Models

End-to-end LLM training:
- Training loop structure
- Mixed precision training
- Gradient accumulation
- Learning rate schedules
- Checkpointing

From theory to practice!
""",
            reference_code="""# Training LLMs - Complete Pipeline
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.amp import autocast, GradScaler

print("Training LLMs - Complete Pipeline")

# Simple Transformer for demonstration
class SimpleLLM(nn.Module):
    def __init__(self, vocab_size, d_model, n_heads, n_layers):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, n_heads, dim_feedforward=d_model*4)
            for _ in range(n_layers)
        ])
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

    def forward(self, input_ids):
        x = self.embedding(input_ids)
        for layer in self.layers:
            x = layer(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        return logits

# Model configuration
vocab_size = 10000
d_model = 256
n_heads = 8
n_layers = 4
batch_size = 8
seq_len = 128

model = SimpleLLM(vocab_size, d_model, n_heads, n_layers)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
print(f"Device: {device}")

# Optimizer and scheduler
optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=1000)

# Mixed precision training
device_type = 'cuda' if torch.cuda.is_available() else 'cpu'
scaler = GradScaler(device_type)

# Gradient accumulation setup
accumulation_steps = 4

# Training function
def train_step(model, batch, optimizer, scaler, step, accumulation_steps):
    input_ids, labels = batch

    # Mixed precision forward pass
    with autocast(device_type=device_type):
        logits = model(input_ids)
        loss = F.cross_entropy(
            logits.view(-1, vocab_size),
            labels.view(-1)
        )
        # Normalize loss for gradient accumulation
        loss = loss / accumulation_steps

    # Backward pass with gradient scaling
    scaler.scale(loss).backward()

    # Update weights every accumulation_steps
    if (step + 1) % accumulation_steps == 0:
        # Gradient clipping
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        # Optimizer step
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()

    return loss.item() * accumulation_steps

# Generate fake batch
def get_batch():
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len)).to(device)
    labels = torch.randint(0, vocab_size, (batch_size, seq_len)).to(device)
    return input_ids, labels

# Training loop
print("\\nTraining demonstration:")
model.train()

for step in range(10):
    batch = get_batch()
    loss = train_step(model, batch, optimizer, scaler, step, accumulation_steps)

    if (step + 1) % accumulation_steps == 0:
        scheduler.step()
        lr = optimizer.param_groups[0]['lr']
        print(f"Step {step+1}: Loss = {loss:.4f}, LR = {lr:.6f}")

# Checkpointing
checkpoint = {
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'scheduler_state_dict': scheduler.state_dict(),
    'scaler_state_dict': scaler.state_dict(),
    'step': 10,
    'loss': loss
}

print(f"\\nCheckpoint created with {len(checkpoint)} keys")

# Inference mode
@torch.no_grad()
def generate(model, input_ids, max_new_tokens=10):
    model.training = False  # Set to inference mode
    for _ in range(max_new_tokens):
        logits = model(input_ids)
        next_token_logits = logits[:, -1, :]
        next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
        input_ids = torch.cat([input_ids, next_token], dim=1)
    return input_ids

# Generate tokens
prompt = torch.randint(0, vocab_size, (1, 10)).to(device)
generated = generate(model, prompt, max_new_tokens=5)
print(f"\\nGenerated sequence length: {generated.shape[1]}")

print("\\nTraining pipeline complete!")
print("Key components:")
print("- Mixed precision (faster training)")
print("- Gradient accumulation (larger effective batch)")
print("- Gradient clipping (stable training)")
print("- Learning rate scheduling")
print("- Checkpointing (save progress)")""",
            learning_objectives=[
                "Build complete training loop",
                "Implement mixed precision training",
                "Use gradient accumulation",
                "Apply learning rate schedules",
                "Save and load checkpoints"
            ],
            hints=[
                "Mixed precision speeds up training",
                "Gradient accumulation simulates larger batches",
                "Always clip gradients for stability",
                "Cosine schedule works well for LLMs",
                "Save checkpoints regularly"
            ],
            visualization_type="neural_network"
        )

        # Session 19: Inference & Generation
        sessions["inference_generation"] = Session(
            id="inference_generation",
            title="🎯 Inference & Generation",
            description="""
# LLM Inference and Text Generation

Generate text with LLMs:
- Greedy decoding
- Beam search
- Temperature sampling
- Top-k and top-p sampling
- Generation strategies

Make your LLM talk!
""",
            reference_code="""# LLM Inference and Generation Strategies
import torch
import torch.nn.functional as F

print("Inference & Generation - Making LLMs Talk")

# Simulate model output (logits)
vocab_size = 100
logits = torch.randn(1, vocab_size)  # (batch=1, vocab_size)

print(f"Logits shape: {logits.shape}")

# 1. Greedy Decoding (simplest)
def greedy_decode(logits):
    return torch.argmax(logits, dim=-1)

greedy_token = greedy_decode(logits)
print(f"\\nGreedy decoding: token {greedy_token.item()}")

# 2. Temperature Sampling
def temperature_sample(logits, temperature=1.0):
    # Higher temperature = more random
    # Lower temperature = more deterministic
    logits = logits / temperature
    probs = F.softmax(logits, dim=-1)
    return torch.multinomial(probs, num_samples=1)

temp_low = temperature_sample(logits, temperature=0.5)
temp_high = temperature_sample(logits, temperature=2.0)
print(f"Low temp (0.5): token {temp_low.item()}")
print(f"High temp (2.0): token {temp_high.item()}")

# 3. Top-k Sampling
def top_k_sample(logits, k=10):
    # Only sample from top k tokens
    top_k_logits, top_k_indices = torch.topk(logits, k)
    probs = F.softmax(top_k_logits, dim=-1)
    sampled_idx = torch.multinomial(probs, num_samples=1)
    return top_k_indices.gather(-1, sampled_idx)

topk_token = top_k_sample(logits, k=10)
print(f"\\nTop-k (k=10): token {topk_token.item()}")

# 4. Top-p (Nucleus) Sampling
def top_p_sample(logits, p=0.9):
    # Sample from smallest set of tokens with cumulative prob > p
    probs = F.softmax(logits, dim=-1)
    sorted_probs, sorted_indices = torch.sort(probs, descending=True)
    cumsum_probs = torch.cumsum(sorted_probs, dim=-1)

    # Remove tokens with cumsum > p
    sorted_indices_to_remove = cumsum_probs > p
    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
    sorted_indices_to_remove[..., 0] = 0

    sorted_probs[sorted_indices_to_remove] = 0
    sorted_probs = sorted_probs / sorted_probs.sum()

    sampled_idx = torch.multinomial(sorted_probs, num_samples=1)
    return sorted_indices.gather(-1, sampled_idx)

topp_token = top_p_sample(logits, p=0.9)
print(f"Top-p (p=0.9): token {topp_token.item()}")

# 5. Beam Search (simplified)
def beam_search(logits_fn, start_token, beam_width=3, max_len=5):
    # logits_fn: function that takes tokens and returns logits
    # Start with initial token
    beams = [(torch.tensor([start_token]), 0.0)]  # (sequence, score)

    for _ in range(max_len):
        candidates = []
        for seq, score in beams:
            if len(seq) >= max_len:
                candidates.append((seq, score))
                continue

            # Get logits for next token
            logits = logits_fn(seq)
            log_probs = F.log_softmax(logits, dim=-1)

            # Get top k next tokens
            top_k_log_probs, top_k_indices = torch.topk(log_probs, beam_width)

            for log_prob, token in zip(top_k_log_probs[0], top_k_indices[0]):
                new_seq = torch.cat([seq, token.unsqueeze(0)])
                new_score = score + log_prob.item()
                candidates.append((new_seq, new_score))

        # Keep top beam_width candidates
        beams = sorted(candidates, key=lambda x: x[1], reverse=True)[:beam_width]

    return beams[0][0]  # Return best sequence

# Example usage (with dummy logits function)
def dummy_logits_fn(seq):
    return torch.randn(1, vocab_size)

beam_result = beam_search(dummy_logits_fn, start_token=0, beam_width=3, max_len=5)
print(f"\\nBeam search result: {beam_result.tolist()}")

# Complete generation function
def generate_text(model, tokenizer, prompt, max_length=50,
                  strategy='top_p', temperature=1.0, top_k=50, top_p=0.9):
    model.training = False  # Set to inference mode
    tokens = tokenizer.encode(prompt)
    generated = torch.tensor(tokens).unsqueeze(0)

    with torch.no_grad():
        for _ in range(max_length):
            logits = model(generated)
            next_token_logits = logits[:, -1, :] / temperature

            if strategy == 'greedy':
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            elif strategy == 'top_k':
                next_token = top_k_sample(next_token_logits, k=top_k)
            elif strategy == 'top_p':
                next_token = top_p_sample(next_token_logits, p=top_p)
            else:
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)

            generated = torch.cat([generated, next_token], dim=1)

            # Stop if end token generated
            if next_token.item() == tokenizer.eos_token_id:
                break

    return tokenizer.decode(generated[0].tolist())

print("\\nGeneration strategies:")
print("- Greedy: Fast but repetitive")
print("- Temperature: Control randomness")
print("- Top-k: Sample from top k tokens")
print("- Top-p: Nucleus sampling (best for quality)")
print("- Beam search: Find high-probability sequences")
print("\\nMost LLMs use top-p sampling!")""",
            learning_objectives=[
                "Understand greedy decoding",
                "Implement temperature sampling",
                "Build top-k and top-p sampling",
                "Create beam search algorithm",
                "Choose generation strategies"
            ],
            hints=[
                "Greedy is deterministic but boring",
                "Temperature controls randomness",
                "Top-k limits vocabulary per step",
                "Top-p (nucleus) is most popular",
                "Beam search finds better sequences"
            ],
            visualization_type="neural_network"
        )

        return sessions
    
    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)
    
    def get_session_list(self) -> List[str]:
        return list(self.sessions.keys())
    
    def mark_session_complete(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id].completed = True
            if session_id not in self.progress.completed_sessions:
                self.progress.completed_sessions.append(session_id)
    
    def get_next_session(self) -> Optional[str]:
        session_order = self.get_session_list()
        try:
            current_index = session_order.index(self.progress.current_session_id)
            if current_index + 1 < len(session_order):
                return session_order[current_index + 1]
        except ValueError:
            pass
        return None