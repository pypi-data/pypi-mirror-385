/*
 * Copyright 2023-2025 NVIDIA Corporation.  All rights reserved.
 *
 * NOTICE TO LICENSEE:
 *
 * This source code and/or documentation ("Licensed Deliverables") are
 * subject to NVIDIA intellectual property rights under U.S. and
 * international Copyright laws.
 *
 * These Licensed Deliverables contained herein is PROPRIETARY and
 * CONFIDENTIAL to NVIDIA and is being provided under the terms and
 * conditions of a form of NVIDIA software license agreement by and
 * between NVIDIA and Licensee ("License Agreement") or electronically
 * accepted by Licensee.  Notwithstanding any terms or conditions to
 * the contrary in the License Agreement, reproduction or disclosure
 * of the Licensed Deliverables to any third party without the express
 * written consent of NVIDIA is prohibited.
 *
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
 * SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
 * PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
 * NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
 * DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
 * NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
 * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
 * LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
 * SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
 * WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
 * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THESE LICENSED DELIVERABLES.
 *
 * U.S. Government End Users.  These Licensed Deliverables are a
 * "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
 * 1995), consisting of "commercial computer software" and "commercial
 * computer software documentation" as such terms are used in 48
 * C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
 * only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
 * 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
 * U.S. Government End Users acquire the Licensed Deliverables with
 * only those rights set forth herein.
 *
 * Any use of the Licensed Deliverables in individual and commercial
 * software must include, in the user documentation and internal
 * comments to the code, the above Disclaimer and U.S. Government End
 * Users Notice.
 */

#ifndef CUDSS_DIST_IFACE_PUBLIC_HEADER_H
#define CUDSS_DIST_IFACE_PUBLIC_HEADER_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum cudssOpType_t {
    CUDSS_SUM,
    CUDSS_MAX,
    CUDSS_MIN
} cudssOpType_t;

/* Interface to communication layer.
 * All send and receive bufferes supposed to be device-accessible so MPI must be CUDA aware
 */
typedef struct {
    int (*cudssCommRank)(void *comm, int *rank);
    int (*cudssCommSize)(void *comm, int *size);
    int (*cudssSend)(const void *buffer, int count, cudaDataType_t datatype, int dest,
        int tag, void *comm, cudaStream_t stream);
    int (*cudssRecv)(void *buffer, int count, cudaDataType_t datatype, int root,
        int tag, void *comm, cudaStream_t stream);
    int (*cudssBcast)(void *buffer, int count, cudaDataType_t datatype,
        int root, void *comm, cudaStream_t stream);
    int (*cudssReduce)(const void *sendbuf, void *recvbuf, int count,
        cudaDataType_t datatype, cudssOpType_t op, int root, void *comm,
        cudaStream_t stream);
    int (*cudssAllreduce)(const void *sendbuf, void *recvbuf, int count,
        cudaDataType_t datatype, cudssOpType_t op, void *comm, cudaStream_t stream);
    int (*cudssScatterv)(const void *sendbuf, const int *sendcounts,
        const int *displs, cudaDataType_t sendtype, void *recvbuf, int recvcount,
        cudaDataType_t recvtype, int root, void *comm, cudaStream_t stream);
    int (*cudssCommSplit)(const void *comm, int color, int key, void *newcomm);
    int (*cudssCommFree)(void *comm);
} cudssDistributedInterface_t;

#ifdef __cplusplus
} /* extern "C" */
#endif
#endif /* CUDSS_DIST_IFACE_PUBLIC_HEADER_H */
