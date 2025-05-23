import os 
import pickle
import numpy as np
from numpy.typing import NDArray 
from typing import Any

# Update paths to use the correct directory structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "python_scripts_and_data", "data")

# Load vocab
with open(os.path.join(DATA_DIR, "foodVocab.pkl"), "rb") as file: 
    vocab = pickle.load(file)

# Load complexRep
with open(os.path.join(DATA_DIR, "complexRep.pkl"), "rb") as file:
    complexRep = pickle.load(file)
    complex_items = list(complexRep.items())

def create_doc_term(complex_items, vocab: list[str], mode:str) -> NDArray[Any]: 
  mode = mode.lower()
  doc_term_rep = np.zeros((len(complex_items), len(vocab)))
  for docIdx, (comment_id, (innerDict, upvotes)) in enumerate(complex_items): 
    #Invariant: Any key of innerDict is guarenteed to be found in vocab
    #f_count_sum = sum(list(innerDict.values())) #Uncomment as needed
    for food, f_count in innerDict.items(): 
      tIdx = vocab.index(food)
      if mode == "bin": 
        doc_term_rep[docIdx][tIdx] = 1
      elif mode == "tf":
        # tf options: 
          # tf = upvotes * f_count (Choosing this for now)
          # tf = upvotes + f_count 
          # tf = upvotes * (f_count/f_count_sum)
        doc_term_rep[docIdx][tIdx] = upvotes * f_count
      else: 
        raise Exception("mode must only equal \"bin\" or \"tf\"")
  return doc_term_rep

def set_jaccard_sim(query, doc_term_mat):
  jaccard_result = np.zeros((len(doc_term_mat), )) 
  doc_term_mat = np.where(doc_term_mat > 0, 1, 0)
  query = np.where(query > 0, 1, 0)
  qNdt = np.dot(doc_term_mat, query.T)
  query_expand = np.tile(query, (len(doc_term_mat), 1))
  qUdt = np.where((doc_term_mat+query_expand) > 0, 1, 0)
  qUdt = np.sum(qUdt, axis=1) #Sum Rowwise

  jaccard_result = qNdt/qUdt
  return jaccard_result

def gen_jaccard_sim(query, doc_term_mat): 
  jaccard_result = np.zeros((len(doc_term_mat), )) 

  w_query = query / np.sum(query)

  w_doc_term_mat = np.zeros(doc_term_mat.shape)
  for rIdx in range(0, len(doc_term_mat)):
    row_sum = np.sum(doc_term_mat[rIdx])
    if row_sum == 0:
        w_row = np.zeros_like(doc_term_mat[rIdx])
    else:
        w_row = doc_term_mat[rIdx] / row_sum

    w_doc_term_mat[rIdx] = w_row

  w_query_expand = np.tile(w_query, (len(w_doc_term_mat), 1))
  max_values = np.maximum(w_query_expand, w_doc_term_mat)
  termWeights = np.where(max_values != 0, np.minimum(w_query_expand, w_doc_term_mat) / max_values, 0)

  query_expand = np.tile(query, (len(doc_term_mat), 1))
  qUdtMask = np.where((doc_term_mat+query_expand) > 0, 1, 0)

  jaccard_result_expand = np.where(qUdtMask > 0, termWeights, 0)

  jaccard_result = np.sum(jaccard_result_expand, axis=1)

  return jaccard_result

doc_term_bin_rep = create_doc_term(complex_items, vocab, mode="bin")
doc_term_tf_rep = create_doc_term(complex_items, vocab, mode="tf")

# sample_query = np.ones((len(vocab),))
# sample_query[0] = 1
# sample_query[10] = 20
# sample_query[50] = 16

# results1 = set_jaccard_sim(sample_query, doc_term_bin_rep)
# results2 = set_jaccard_sim(sample_query, doc_term_tf_rep)

# results3 = gen_jaccard_sim(sample_query, doc_term_bin_rep)
# results4 = gen_jaccard_sim(sample_query, doc_term_tf_rep)

# print(results1)
# print(results2)
# print(results3)
# print(results4)