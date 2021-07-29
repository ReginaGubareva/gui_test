import os  # handle file joining operation for model
import tensorflow.keras as keras
from tensorflow.keras.layers import Dense  # our layers
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow.keras.optimizers import Adam


class ActorCriticNetwork(keras.Model):
    def __init__(self, n_actions, fc1_dims=1296, fc2_dims=696,
                 name='actor_critic', chkpt_dir='tmp/actor_critic'):
        super(ActorCriticNetwork, self).__init__()
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.model_name = name
        self.checkpoint_dir = chkpt_dir
        self.checkpoint_file = os.path.join(chkpt_dir, self.model_name + '_ac')

        self.fc1 = Dense(self.fc1_dims, activation='relu')
        self.fc2 = Dense(self.fc2_dims, activation='relu')
        self.v = Dense(1, activation=None)
        self.pi = Dense(2, activation='softmax')

    def call(self, state):
        value = self.fc1(state)
        value = self.fc2(value)
        v = self.v(value)
        pi = self.pi(value)

        return v, pi


class Agent:
    def __init__(self, alpha=0.0003, gamma=0.99, n_actions=2):
        self.gamma = gamma
        self.n_actions = n_actions
        self.action = None
        self.action_space = [i for i in range(self.n_actions)]
        self.actor_critic = ActorCriticNetwork(n_actions=n_actions)
        self.actor_critic.compile(optimizer=Adam(learning_rate=alpha))

    def choose_action(self, observation):
        print('obs shape', observation.shape)
        # action_space = ['click', 'type']
        # state = tf.keras.preprocessing.image.img_to_array(observation)
        state = self.convert_img_to_tensor(observation)
        state = tf.convert_to_tensor(state)
        _, probs = self.actor_critic(state)
        action_probabilities = tfp.distributions.Categorical(probs=probs)
        action = action_probabilities.sample()
        log_prob = action_probabilities.log_prob(action)
        self.action = action
        # print('action:', action.shape)
        return action

    def save_models(self):
        print('... saving models ...')
        self.actor_critic.save_weights(self.actor_critic.checkpoint_file)

    def load_models(self):
        print('Loading models')
        self.actor_critic.load_weights(self.actor_critic.checkpoint_file)

    def learn(self, state, reward, state_, done):
        # state = tf.convert_to_tensor([state], dtype=tf.float32)
        state = self.convert_img_to_tensor(state)
        state = tf.convert_to_tensor(state)

        state_ = self.convert_img_to_tensor(state_)
        state_ = tf.convert_to_tensor(state_)

        reward = tf.convert_to_tensor(reward, dtype=tf.float32)

        with tf.GradientTape(persistent=True) as tape:
            state_value, probs = self.actor_critic(state)
            state_value_, _ = self.actor_critic(state_)

            state_value = tf.squeeze(state_value)
            state_value_ = tf.squeeze(state_value_)

            action_probs = tfp.distributions.Categorical(probs=probs)
            log_prob = action_probs.log_prob(self.action)

            delta = reward + self.gamma * state_value_ * (1 - int(done)) - state_value
            actor_loss = -log_prob * delta
            critic_loss = delta ** 2
            total_loss = actor_loss + critic_loss

        gradient = tape.gradient(total_loss, self.actor_critic.trainable_variables)
        self.actor_critic.optimizer.apply_gradients(zip(
            gradient, self.actor_critic.trainable_variables))

    @staticmethod
    def convert_img_to_tensor(state):
        state = np.array(state)
        shape = state.shape
        # normalized_metrics = normalize(state, axis=0, norm='l1')
        flat_arr = state.ravel()
        result_arr = []
        # print('normalized metrics: ', normalized_metrics)
        return state
