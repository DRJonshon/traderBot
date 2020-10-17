# -*- coding: utf-8 -*-
#réseau de neurones type LSTM, avec une couche linéaire en sortie

print('paramétrage des modules python...')

import torch
import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.preprocessing import MinMaxScaler
from pandas.plotting import register_matplotlib_converters
from torch import nn, optim
from datetime import datetime


#paramètres de base pour les graphiques et le hasard
sns.set(style='whitegrid', palette='muted', font_scale=1.2)
HAPPY_COLORS_PALETTE = ["#01BEFE", "#FFDD00", "#FF7D00", "#FF006D", "#93D30C", "#8F00FF"]
sns.set_palette(sns.color_palette(HAPPY_COLORS_PALETTE))

rcParams['figure.figsize'] = 14, 10
register_matplotlib_converters()

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)


class SequencePredictor(nn.Module):

  def __init__(self, n_features, n_hidden, seq_len, n_layers=2):
    super().__init__()

    self.n_hidden = n_hidden
    self.seq_len = seq_len
    self.n_layers = n_layers

    self.lstm = nn.LSTM(
      input_size=n_features, #le nombre de paramètres en entrée
      hidden_size=n_hidden, #la taille de la couche cachée
      num_layers=n_layers, #le nombre de couches cachées
      dropout=0.5 #altération de l'entrée pour un meilleur entraînement: https://arxiv.org/abs/1207.0580
    )

    self.linear = nn.Linear(in_features=n_hidden, out_features=1) #pour ramener la sortie à une valeur

  def reset_hidden_state(self):
    self.hidden = (
        torch.zeros(self.n_layers, self.seq_len, self.n_hidden),
        torch.zeros(self.n_layers, self.seq_len, self.n_hidden)
    )

  def forward(self, sequences): #le module PyTorch s'occupe de tout
    lstm_out, self.hidden = self.lstm(
      sequences.view(len(sequences), self.seq_len, -1),
      self.hidden
    )
    last_time_step = \
      lstm_out.view(self.seq_len, len(sequences), self.n_hidden)[-1]
    y_pred = self.linear(last_time_step)
    return y_pred

def train_model(
  model,
  train_data,
  train_labels,
  test_data=None,
  test_labels=None
):
  loss_fn = torch.nn.MSELoss(reduction='sum')#somme des carrés des différences

  optimiser = torch.optim.Adam(model.parameters(), lr=1e-3)# https://arxiv.org/abs/1412.6980
  num_epochs = 10

  train_hist = np.zeros(num_epochs)
  test_hist = np.zeros(num_epochs)

  for t in range(num_epochs):
    model.reset_hidden_state()

    y_pred = model(X_train)

    loss = loss_fn(y_pred.float(), y_train)

    if test_data is not None:
      with torch.no_grad():
        y_test_pred = model(X_test)
        test_loss = loss_fn(y_test_pred.float(), y_test)
      test_hist[t] = test_loss.item()

      if t % 1 == 0:
        print(f'Epoch {t} train loss: {loss.item()} test loss: {test_loss.item()}')
    elif t % 1 == 0:
      print(f'Epoch {t} train loss: {loss.item()}')

    train_hist[t] = loss.item()

    optimiser.zero_grad()

    loss.backward()

    optimiser.step()

  return model.eval(), train_hist, test_hist

def create_sequences(data, seq_length):
    xs = []
    ys = []

    for i in range(len(data)-seq_length-1):
        x = data[i:(i+seq_length)]
        y = data[i+seq_length]
        xs.append(x)
        ys.append(y)

    return np.array(xs), np.array(ys)


#reste à formatter train_data et test_data
print('pré-traitement des données...')
timestamps = []
close_2h = []
with open('../data/10.json','rb') as file:
    data = json.load(file)
for d in data:
    date = str(datetime.fromtimestamp(d['date']))

    timestamps.append(date)
    close_2h.append(d['close'])

test_data_size = 360

train_data = close_2h[:-test_data_size]
test_data = close_2h[-test_data_size:]

scaler = MinMaxScaler()

scaler = scaler.fit(np.expand_dims(train_data, axis=1))

train_data = scaler.transform(np.expand_dims(train_data, axis=1))

test_data = scaler.transform(np.expand_dims(test_data, axis=1))

#formatage
seq_length = 5
X_train, y_train = create_sequences(train_data, seq_length)
X_test, y_test = create_sequences(test_data, seq_length)

X_train = torch.from_numpy(X_train).float()
y_train = torch.from_numpy(y_train).float()

X_test = torch.from_numpy(X_test).float()
y_test = torch.from_numpy(y_test).float()

model = SequencePredictor(
  n_features=1, #nombre d'indicateurs en entrée, ici juste le prix.
  n_hidden=128,
  seq_len=seq_length,
  n_layers=2
)

print("démarrage de l'entraînement...")
model, train_hist, test_hist = train_model(
  model,
  X_train,
  y_train,
  X_test,
  y_test
)

print('entraînement terminé.')
plt.plot(train_hist, label="Training loss")
plt.plot(test_hist, label="Test loss")
plt.legend();
plt.show()

with torch.no_grad():
  test_seq = X_test[:1]
  preds = []
  for _ in range(len(X_test)):
    y_test_pred = model(test_seq)
    pred = torch.flatten(y_test_pred).item()
    preds.append(pred)
    new_seq = test_seq.numpy().flatten()
    new_seq = np.append(new_seq, [pred])
    new_seq = new_seq[1:]
    test_seq = torch.as_tensor(new_seq).view(1, seq_length, 1).float()

true_cases = scaler.inverse_transform(
    np.expand_dims(y_test.flatten().numpy(), axis=0)
).flatten()

predicted_cases = scaler.inverse_transform(
  np.expand_dims(preds, axis=0)
).flatten()

#plt.plot(
#  timestamps[:len(train_data)],
#  scaler.inverse_transform(train_data).flatten(),
#  label='Historical Close value'
#)

plt.plot(
  timestamps[len(train_data):len(train_data) + len(true_cases)],
  true_cases,
  label='Real Close Value'
)

plt.plot(
  timestamps[len(train_data):len(train_data) + len(true_cases)],
  predicted_cases,
  label='Predicted Close Value'
)

plt.legend();
plt.show()
print('end of script. press enter to Exit')
input()
